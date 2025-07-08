import { Routes, Route } from 'react-router-dom'
import { 
  AppShell, 
  Container,
  Title,
  Group,
  Burger,
} from '@mantine/core'
import { useDisclosure } from '@mantine/hooks'
import { IconTower } from '@tabler/icons-react'
import Dashboard from './pages/Dashboard'

function App() {
  const [opened, { toggle }] = useDisclosure();

  return (
    <AppShell
      header={{ height: 60 }}
      navbar={{
        width: 300,
        breakpoint: 'sm',
        collapsed: { mobile: !opened },
      }}
      padding="md"
    >
      <AppShell.Header>
        <Group h="100%" px="md">
          <Burger opened={opened} onClick={toggle} hiddenFrom="sm" size="sm" />
          <Group>
            <IconTower size={28} />
            <Title order={3}>Tower Jumps</Title>
          </Group>
        </Group>
      </AppShell.Header>

      <AppShell.Main>
        <Container fluid>
          <Routes>
            <Route path="/" element={<Dashboard />} />
          </Routes>
        </Container>
      </AppShell.Main>
    </AppShell>
  )
}

export default App
