import { Container, Title, Text, Button, Select} from '@mantine/core'
import { useState, useEffect } from 'react'
import { useForm } from '@mantine/form';
import { DateTimePicker } from '@mantine/dates';

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
    pings: any;
}

function Dashboard() {
    const [subscribers, setSubscribers] = useState<Subscriber[]>([])
    const [inferenceResult, setInferenceResult] = useState<InferenceResponse | null>(null)
    const [query, setQuery] = useState<string>('');

    const MODELS = [
        { value: "1", label: 'Majority Vote' },
        { value: "2", label: 'Clustering' },
    ]

    const form = useForm({
        initialValues: {
            subscriberId: '',
            startTime: null,
            endTime: null,
            model: '1'
        },
        validate: {
            subscriberId: (value) => (value ? null : 'Subscriber is required'),
            model: (value) => (value ? null : 'Model selection is required'),
        },
    })

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

    const handleSubmit = async (values: typeof form.values) => {
        try {
        const params = new URLSearchParams()
        if (values.startTime) {
          params.append('start', values.startTime.toISOString())
        }
        if (values.endTime) {
          params.append('end', values.endTime.toISOString())
        }
        params.append('model', values.model)
        const response = await fetch(`/api/subscribers/${values.subscriberId}/infer/?${params.toString()}`)
        if (!response.ok) {
          throw new Error('Failed to fetch subscribers')
        }
        const data = await response.json()
        setInferenceResult(data)
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
            <Text mt="md" size="sm" color="dimmed">{inferenceResult ? `Inference Result: ${JSON.stringify(inferenceResult)}` : 'No inference result yet'}</Text>
        </Container>
    )
}

export default Dashboard
