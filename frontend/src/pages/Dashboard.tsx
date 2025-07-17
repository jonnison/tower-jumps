import { Container, Title, Text, Button, Select} from '@mantine/core'
import { useState, useEffect } from 'react'
import { useForm } from '@mantine/form';
import { DateTimePicker } from '@mantine/dates';
import { Card } from '@mantine/core';
import { MapContainer, TileLayer, Marker, Popup, Circle , useMap } from 'react-leaflet';
import L from 'leaflet';

type Subscriber = {
    id: number; 
    name: string;
}

type InferenceResponse = {
    interval_start: string,
    interval_end: string,
    ping_count: number,
    confidence_pct: string,
    method: number,
    subscriber: number,
    state: string,
    pings: Array<{
        geom: string,
        cell_type: string,
        utc_time: string,
        state: string,
        coordinates?: [number, number],
    }>;
}

const ICONS = {
    'Data': L.icon({
        iconUrl: '/icons/data.svg',
        iconSize: [24, 24],
    }),
    'Voice': L.icon({
        iconUrl: '/icons/phone-call.svg',
        iconSize: [24, 24],
    }),
    'SMS': L.icon({
        iconUrl: '/icons/sms.svg',
        iconSize: [24, 24],
    }),
}

function Dashboard() {
    const [subscribers, setSubscribers] = useState<Subscriber[]>([])
    const [query, setQuery] = useState<string>('');
    const [inferenceResult, setInferenceResult] = useState<InferenceResponse | null>(null);
    const [color, setColor] = useState<string>('blue');
    const MODELS = [
        { value: "1", label: 'Majority Vote' },
        { value: "2", label: 'Clustering' },
    ]

    const form = useForm({
        initialValues: {
            subscriberId: 12,
            startTime: new Date('2024-11-26T00:00:00.000Z'),
            endTime: new Date('2024-11-26T05:00:00.000Z'),
            model: '1'
        },
        validate: {
            subscriberId: (value) => (value ? null : 'Subscriber is required'),
            model: (value) => (value ? null : 'Model selection is required'),
        },
    })

    const parseGeomToLatLng = (geom: string): [number, number] => {
        // Example geom: "SRID=4326;POINT (-73.57165 41.22256)"
        const match = geom.match(/POINT\s*\(\s*([-\d.]+)\s+([-\d.]+)\s*\)/);
        if (match) {
            // Note: POINT (lng lat)
            const lng = parseFloat(match[1]);
            const lat = parseFloat(match[2]);
            return [lat, lng];
        }
        // fallback to [0,0] if parsing fails
        return [0, 0];
    }

    const fetchSubscribers = async () => {
      try {
        const params = new URLSearchParams()
        if (query) {
          params.append('name', query)
        }
        const response = await fetch(`/api/subscribers/?${params.toString()}`)
        if (!response.ok) {
          throw new Error('Failed to fetch subscribers')
        }
        const data = await response.json()
        setSubscribers(data)
      } catch (error) {
        console.error('Error fetching subscribers:', error)
      }
    }

    useEffect(() => {
        fetchSubscribers()
    }, [])

    useEffect(() => {
        fetchSubscribers()
    }, [query])

    const colorPalette = ((confidence: string) => {
        const pct = parseFloat(confidence);
        if (pct >= 80) return 'green';
        if (pct >= 60) return 'yellow';
        if (pct >= 40) return 'orange';
        return 'red';
    });

    const handleSubmit = async (values: typeof form.values) => {
        try {
        const params = new URLSearchParams()
        if (values.startTime) {
          params.append('start', values.startTime.toISOString())
        }
        if (values.endTime) {
          params.append('end', values.endTime.toISOString())
        }
        params.append('model_id', values.model)
        const response = await fetch(`/api/subscribers/${values.subscriberId}/infer/?${params.toString()}`)
        if (!response.ok) {
          throw new Error('Failed to fetch subscribers')
        }
        const data = await response.json()
        data.pings = data.pings.map((ping: any) => ({
          ...ping,
          coordinates: parseGeomToLatLng(ping.geom),
        }))
        data.pings = data.pings.filter((ping: any) => ping.coordinates && ping.coordinates.length === 2);
        data.pings = data.pings.slice(0, 100); // Limit to 100 pings for performance
        setInferenceResult(data)
        setColor(colorPalette(data.confidence_pct));
      } catch (error) {
        console.error('Error fetching subscribers:', error)
      }
    }

    return (
        <Container size="xl">
            <Title order={1} mb="xl">User Location Confidence</Title>
            
            <form onSubmit={form.onSubmit(handleSubmit)}>
                <Select
                    label="Search Subscriber"
                    placeholder="Type to search..."
                    searchable
                    nothingFoundMessage="No subscribers found"
                    data={subscribers.map(sub => ({ value: sub.id.toString(), label: sub.name }))}                
                    onSearchChange={setQuery}
                    searchValue={query}

                    {...form.getInputProps('subscriberId')}
                />
                <DateTimePicker label="Start Time" placeholder="Select start time for analysis" {...form.getInputProps('startTime')} />
                <DateTimePicker label="End Time" placeholder="Select end time for analysis" {...form.getInputProps('endTime')} />
                <Select
                    label="Search model"
                    placeholder="Type to search..."
                    data={MODELS}
                    {...form.getInputProps('model')}
                />
                <Button type="submit" mt="md">Search</Button>
            </form>
            {(inferenceResult && inferenceResult.pings.length > 0) && (
               <Card shadow="sm" padding="lg" radius="md" withBorder>
                <Text fw={500} size="lg" mt="md">
                  Predicted state: {inferenceResult.state} ({inferenceResult.confidence_pct}% confidence) 
                </Text>
                <Card.Section>
                  <div style={{ height: '400px' }}>
                    <MapContainer 
                      center={[41.2033, -77.1945]} // Default center (Pennsylvania)
                      zoom={10}
                      style={{ height: '100%', width: '100%' }}
                      >
                      
                        <TileLayer
                          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        />
                        {inferenceResult.pings.map((ping: any, index: number) => (
                          <Marker 
                            key={index} 
                            position={ping.coordinates}
                            icon={ ICONS[ping.cell_type as keyof typeof ICONS] }
                            >
                              <Popup>
                                <Text>State: {ping.state}</Text>
                                <Text>Timestamp: {new Date(ping.utc_time).toLocaleString()}</Text>
                              </Popup>
                          </Marker>
                        ))}
                        <GroupPings pings={inferenceResult.pings} color={color} />
                    </MapContainer>
                  </div>
                </Card.Section>
              </Card>
            )}
        </Container>
    )
}

function GroupPings({ pings, color }: { pings: any[], color?: string }) {
  const map = useMap();

  const bounds = L.latLngBounds(pings.map(ping => L.latLng(ping.coordinates[0], ping.coordinates[1])));
  const center = bounds.getCenter();
  const radius = bounds.getNorthEast().distanceTo(bounds.getSouthWest()) / 2;
  map.fitBounds(bounds, { padding: [30, 30] });

  color = color || 'blue';

  return (
    <Circle
      center={center}
      radius={radius}
      pathOptions={{ color, fillOpacity: 0.1 }}
    />
  );
}
export default Dashboard
