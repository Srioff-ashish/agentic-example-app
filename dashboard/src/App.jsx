import { useState, useEffect, useRef } from 'react';
import { Activity, Truck, CheckCircle, AlertCircle, Users } from 'lucide-react';
import './App.css';

function App() {
  const [isConnected, setIsConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [agents, setAgents] = useState([]);
  const [stats, setStats] = useState({
    shipmentsProcessed: 0,
    activeAgents: 0,
    complianceChecks: 0,
  });
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket
    const connectWebSocket = () => {
      const ws = new WebSocket('ws://localhost:8000/ws');
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
      };
      
      ws.onmessage = (event) => {
        const message = JSON.parse(event.data);
        console.log('Received message:', message);
        
        // Add event to the list
        setEvents(prev => [{
          ...message,
          id: Date.now() + Math.random(),
        }, ...prev].slice(0, 50)); // Keep last 50 events
        
        // Update stats based on event type
        if (message.type === 'shipment_processing_completed') {
          setStats(prev => ({
            ...prev,
            shipmentsProcessed: prev.shipmentsProcessed + 1,
          }));
        } else if (message.type === 'agent_connected') {
          setStats(prev => ({
            ...prev,
            activeAgents: prev.activeAgents + 1,
          }));
        } else if (message.type === 'agent_task_completed' && 
                   message.data?.agent === 'compliance') {
          setStats(prev => ({
            ...prev,
            complianceChecks: prev.complianceChecks + 1,
          }));
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };
      
      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        // Reconnect after 3 seconds
        setTimeout(connectWebSocket, 3000);
      };
      
      wsRef.current = ws;
    };
    
    connectWebSocket();
    
    // Fetch agents list
    fetchAgents();
    
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('http://localhost:8000/agents');
      const data = await response.json();
      setAgents(data.agents || []);
      setStats(prev => ({
        ...prev,
        activeAgents: data.agents?.length || 0,
      }));
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    }
  };

  const getEventIcon = (type) => {
    if (type?.includes('completed') || type?.includes('connected')) {
      return <CheckCircle className="event-icon success" />;
    } else if (type?.includes('failed') || type?.includes('error')) {
      return <AlertCircle className="event-icon error" />;
    } else if (type?.includes('started') || type?.includes('processing')) {
      return <Activity className="event-icon processing" />;
    }
    return <Activity className="event-icon" />;
  };

  const formatEventType = (type) => {
    return type?.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) || 'Event';
  };

  return (
    <div className="App">
      <header className="header">
        <div className="header-content">
          <div className="logo">
            <Truck size={32} />
            <h1>Supply Chain Dashboard</h1>
          </div>
          <div className="connection-status">
            <div className={`status-indicator ${isConnected ? 'connected' : 'disconnected'}`} />
            <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
          </div>
        </div>
      </header>

      <main className="main-content">
        {/* Stats Cards */}
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-icon">
              <Truck size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.shipmentsProcessed}</div>
              <div className="stat-label">Shipments Processed</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">
              <Users size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.activeAgents}</div>
              <div className="stat-label">Active Agents</div>
            </div>
          </div>
          
          <div className="stat-card">
            <div className="stat-icon">
              <CheckCircle size={24} />
            </div>
            <div className="stat-content">
              <div className="stat-value">{stats.complianceChecks}</div>
              <div className="stat-label">Compliance Checks</div>
            </div>
          </div>
        </div>

        <div className="content-grid">
          {/* Agents List */}
          <div className="panel">
            <h2 className="panel-title">
              <Users size={20} />
              Connected Agents
            </h2>
            <div className="agents-list">
              {agents.length > 0 ? (
                agents.map((agent, index) => (
                  <div key={index} className="agent-item">
                    <div className="agent-info">
                      <div className="agent-name">{agent.name}</div>
                      <div className="agent-type">{agent.agent_type}</div>
                    </div>
                    <div className="agent-status">
                      <div className="status-indicator connected" />
                      {agent.status}
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">No agents connected</div>
              )}
            </div>
          </div>

          {/* Events Stream */}
          <div className="panel events-panel">
            <h2 className="panel-title">
              <Activity size={20} />
              Real-time Events
            </h2>
            <div className="events-list">
              {events.length > 0 ? (
                events.map((event) => (
                  <div key={event.id} className="event-item">
                    {getEventIcon(event.type)}
                    <div className="event-content">
                      <div className="event-type">{formatEventType(event.type)}</div>
                      <div className="event-data">
                        {event.data && (
                          <pre>{JSON.stringify(event.data, null, 2)}</pre>
                        )}
                      </div>
                      {event.timestamp && (
                        <div className="event-timestamp">
                          {new Date(event.timestamp).toLocaleTimeString()}
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : (
                <div className="empty-state">
                  <Activity size={48} />
                  <p>Waiting for events...</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
