import React, { useState, useEffect } from 'react';
import ReactFlow, { Background, Controls, MarkerType } from 'reactflow';
import 'reactflow/dist/style.css';
import { useNeuro } from "../context/NeuroProvider";

const initialNodes = [
  { id: 'Home', position: { x: 250, y: 0 }, data: { label: '🏠 Home' }, style: { backgroundColor: '#fff' } },
  { id: 'Products', position: { x: 100, y: 100 }, data: { label: '📦 Products' } },
  { id: 'Profile', position: { x: 400, y: 100 }, data: { label: '👤 Profile' } },
  { id: 'HoneyPot', position: { x: 250, y: -100 }, data: { label: '⚠️ /api/admin/debug' }, style: { backgroundColor: '#fee2e2', border: '1px solid red' } },
];

const initialEdges = [
  { id: 'e-h-prod', source: 'Home', target: 'Products', animated: true },
  { id: 'e-h-prof', source: 'Home', target: 'Profile', animated: true },
  { id: 'e-trap', source: 'Home', target: 'HoneyPot', animated: true, style: { stroke: 'red' }, markerEnd: { type: MarkerType.ArrowClosed, color: 'red' } },
];

export function AdminPanel() {
  const { suspicionScore } = useNeuro();
  const [nodes, setNodes] = useState(initialNodes);
  const [edges, setEdges] = useState(initialEdges);

  const activePath = 'Home';

  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => {
        if (node.id === activePath) {
          node.style = { ...node.style, backgroundColor: '#dcfce3', border: '2px solid #22c55e', boxShadow: '0 0 15px rgba(34, 197, 94, 0.4)' };
        } else if (node.id === 'HoneyPot') {
          node.style = { ...node.style, backgroundColor: suspicionScore > 0.9 ? '#ef4444' : '#fee2e2' };
        } else {
          node.style = { ...node.style, backgroundColor: '#fff', border: '1px solid #eee', boxShadow: 'none' };
        }
        return node;
      })
    );
  }, [activePath, suspicionScore]);

  return (
    <div className="h-screen w-full flex bg-gray-50">
      <div className="w-2/3 h-full p-4">
        <h2 className="text-xl font-bold mb-4 font-mono text-gray-800">God-View: Realtime DAG Visualization</h2>
        <div className="bg-white border rounded-xl shadow-inner h-[500px]">
          <ReactFlow nodes={nodes} edges={edges} fitView>
            <Background color="#ccc" gap={16} />
            <Controls />
          </ReactFlow>
        </div>
      </div>
      <div className="w-1/3 p-4 bg-gray-900 text-green-400 font-mono shadow-xl z-10 overflow-hidden">
         <h2 className="text-2xl mb-6">Threat Cortex</h2>
         <div className="bg-black p-4 rounded mb-6">
             <div className="text-sm text-gray-400">Current Session Suspicion</div>
             <div className={`text-6xl ${suspicionScore > 0.7 ? 'text-red-500' : 'text-green-500'}`}>
                 {(suspicionScore * 100).toFixed(1)}%
             </div>
         </div>
         <div className="h-64 overflow-y-auto text-xs opacity-70">
            <div>&gt; [INGEST] PACKET_ACK: velocity=142ms, node=Products</div>
            {suspicionScore > 0.7 && <div className="text-red-500">&gt; [ML_PREDICT] ANOMALY DETECTED. Human Confidence: 12%</div>}
         </div>
      </div>
    </div>
  );
}
import React, { useState, useEffect, useCallback } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MarkerType,
  useNodesState,
  useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';
import { useNeuro } from "../context/NeuroProvider";
import { motion } from 'framer-motion';

/**
 * AdminPanel - God-View Dashboard
 * Real-time monitoring of DAG paths, suspicion scores, and event streams
 */

// Initial DAG structure
const initialNodes = [
  {
    id: 'Home',
    position: { x: 250, y: 0 },
    data: { label: '🏠 Home' },
    style: {
      backgroundColor: '#ffffff',
      border: '2px solid #e5e7eb',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '12px',
      fontWeight: 'bold',
    },
  },
  {
    id: 'Products',
    position: { x: 100, y: 120 },
    data: { label: '📦 Products' },
    style: {
      backgroundColor: '#ffffff',
      border: '2px solid #e5e7eb',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '12px',
      fontWeight: 'bold',
    },
  },
  {
    id: 'Profile',
    position: { x: 400, y: 120 },
    data: { label: '👤 Profile' },
    style: {
      backgroundColor: '#ffffff',
      border: '2px solid #e5e7eb',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '12px',
      fontWeight: 'bold',
    },
  },
  {
    id: 'HoneyPot',
    position: { x: 250, y: -100 },
    data: { label: '⚠️ /api/admin/debug' },
    style: {
      backgroundColor: '#fee2e2',
      border: '2px solid #ef4444',
      borderRadius: '8px',
      padding: '10px',
      fontSize: '12px',
      fontWeight: 'bold',
      color: '#991b1b',
    },
  },
];

const initialEdges = [
  {
    id: 'e-h-prod',
    source: 'Home',
    target: 'Products',
    animated: true,
    markerEnd: { type: MarkerType.ArrowClosed },
    style: { stroke: '#60a5fa', strokeWidth: 2 },
  },
  {
    id: 'e-h-prof',
    source: 'Home',
    target: 'Profile',
    animated: true,
    markerEnd: { type: MarkerType.ArrowClosed },
    style: { stroke: '#60a5fa', strokeWidth: 2 },
  },
  {
    id: 'e-trap',
    source: 'Home',
    target: 'HoneyPot',
    animated: true,
    style: { stroke: '#ef4444', strokeWidth: 2, strokeDasharray: '5,5' },
    markerEnd: { type: MarkerType.ArrowClosed, color: '#ef4444' },
  },
];

export function AdminPanel() {
  const { suspicionScore, isConnected, socket } = useNeuro();
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [eventStream, setEventStream] = useState([]);
  const [activePath, setActivePath] = useState('Home');

  // Update node styles based on suspicion and active path
  useEffect(() => {
    setNodes((nds) =>
      nds.map((node) => {
        let newStyle = { ...node.style };

        // Glow green if user is on this node
        if (node.id === activePath && activePath !== 'HoneyPot') {
          newStyle = {
            ...newStyle,
            backgroundColor: '#dcfce3',
            border: '2px solid #22c55e',
            boxShadow: '0 0 15px rgba(34, 197, 94, 0.5)',
          };
        }
        // Glow red if trap is active
        else if (node.id === 'HoneyPot' && suspicionScore > 0.9) {
          newStyle = {
            ...newStyle,
            backgroundColor: '#fee2e2',
            border: '3px solid #dc2626',
            boxShadow: '0 0 20px rgba(220, 38, 38, 0.7)',
          };
        }
        // Reset to default
        else if (node.id === 'HoneyPot') {
          newStyle = {
            ...newStyle,
            backgroundColor: '#fee2e2',
            border: '2px solid #ef4444',
          };
        } else {
          newStyle = {
            ...newStyle,
            backgroundColor: '#ffffff',
            border: '2px solid #e5e7eb',
            boxShadow: 'none',
          };
        }

        return { ...node, style: newStyle };
      })
    );
  }, [activePath, suspicionScore, setNodes]);

  // Log events to stream
  const addEvent = useCallback((event) => {
    setEventStream((prev) => [
      { id: Math.random(), ...event, timestamp: new Date().toLocaleTimeString() },
      ...prev.slice(0, 49), // Keep last 50 events
    ]);
  }, []);

  // Listen for real-time updates from backend
  useEffect(() => {
    if (!socket) return;

    const handleUICommand = (data) => {
      addEvent({
        type: 'UI_COMMAND',
        message: `Density: ${data.value} | Reason: ${data.reason}`,
        severity: 'info',
      });
    };

    const handleActionAck = (data) => {
      setActivePath(data.currentPath || 'Home');
      addEvent({
        type: 'ACTION_ACK',
        message: `Risk: ${(data.suspicionScore * 100).toFixed(1)}% | ML Confidence: ${data.mlConfidence?.toFixed(1)}%`,
        severity: data.isPotentialBot ? 'warning' : 'success',
      });
    };

    socket.on('UI_COMMAND', handleUICommand);
    socket.on('action_ack', handleActionAck);

    return () => {
      socket.off('UI_COMMAND', handleUICommand);
      socket.off('action_ack', handleActionAck);
    };
  }, [socket, addEvent]);

  return (
    <div className="w-full h-screen flex bg-gray-900 text-gray-100 font-mono">
      {/* DAG Visualization */}
      <div className="w-2/3 h-full flex flex-col bg-gray-800 border-r border-gray-700">
        <div className="p-4 bg-gray-900 border-b border-gray-700">
          <h2 className="text-xl font-bold text-green-400">🧠 NeuroUX God-View: Realtime DAG</h2>
          <p className="text-xs text-gray-400 mt-1">Connected: {isConnected ? '✅ Yes' : '❌ No'}</p>
        </div>
        <div className="flex-1 bg-gray-800">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            fitView
          >
            <Background color="#333" gap={16} />
            <Controls />
          </ReactFlow>
        </div>
      </div>

      {/* Right Panel: Metrics & Event Stream */}
      <div className="w-1/3 h-full flex flex-col bg-gray-900 border-l border-gray-700">
        {/* Suspicion Threat Cortex */}
        <motion.div
          className="p-4 bg-gray-800 border-b border-gray-700"
          animate={{ borderColor: suspicionScore > 0.7 ? '#ef4444' : '#10b981' }}
        >
          <h3 className="text-sm font-bold text-yellow-400 mb-3">⚠️ THREAT CORTEX</h3>

          {/* Suspicion Gauge */}
          <div className="bg-gray-900 p-3 rounded border border-gray-700 mb-3">
            <div className="text-xs text-gray-400 mb-1">Suspicion Score</div>
            <div className="flex items-baseline gap-2">
              <div
                className={`text-5xl font-bold ${
                  suspicionScore > 0.8
                    ? 'text-red-500'
                    : suspicionScore > 0.5
                      ? 'text-yellow-500'
                      : 'text-green-500'
                }`}
              >
                {(suspicionScore * 100).toFixed(1)}%
              </div>
              <div className="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden">
                <motion.div
                  className={`h-full ${
                    suspicionScore > 0.8
                      ? 'bg-red-500'
                      : suspicionScore > 0.5
                        ? 'bg-yellow-500'
                        : 'bg-green-500'
                  }`}
                  animate={{ width: `${suspicionScore * 100}%` }}
                  transition={{ duration: 0.5 }}
                />
              </div>
            </div>
          </div>

          {/* Status Indicators */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-gray-900 p-2 rounded border border-gray-700">
              <div className="text-gray-400">Status</div>
              <div className={suspicionScore > 0.8 ? 'text-red-400 font-bold' : 'text-green-400 font-bold'}>
                {suspicionScore > 0.8 ? '🚨 ALERT' : suspicionScore > 0.5 ? '⚠️ CAUTION' : '✅ SAFE'}
              </div>
            </div>
            <div className="bg-gray-900 p-2 rounded border border-gray-700">
              <div className="text-gray-400">Current Node</div>
              <div className="text-blue-400 font-bold">{activePath}</div>
            </div>
          </div>
        </motion.div>

        {/* Event Stream */}
        <div className="flex-1 flex flex-col bg-gray-800 overflow-hidden border-b border-gray-700">
          <div className="p-2 bg-gray-900 border-b border-gray-700">
            <h3 className="text-xs font-bold text-cyan-400">📡 LIVE EVENT STREAM</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-2 space-y-1 scrollbar-thin scrollbar-thumb-gray-600">
            {eventStream.length === 0 ? (
              <div className="text-gray-500 text-xs">Waiting for events...</div>
            ) : (
              eventStream.map((event) => (
                <motion.div
                  key={event.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  className={`text-xs p-1 rounded border-l-2 ${
                    event.severity === 'warning'
                      ? 'border-yellow-500 text-yellow-300 bg-yellow-900 bg-opacity-20'
                      : event.severity === 'success'
                        ? 'border-green-500 text-green-300 bg-green-900 bg-opacity-20'
                        : 'border-blue-500 text-blue-300 bg-blue-900 bg-opacity-20'
                  }`}
                >
                  <div className="flex justify-between">
                    <span className="font-bold">[{event.type}]</span>
                    <span className="text-gray-500">{event.timestamp}</span>
                  </div>
                  <div className="text-xs truncate">{event.message}</div>
                </motion.div>
              ))
            )}
          </div>
        </motion.div>

        {/* Footer */}
        <div className="p-2 bg-gray-900 border-t border-gray-700 text-xs text-gray-500">
          <div>Events: {eventStream.length} | Status: {isConnected ? 'Connected' : 'Disconnected'}</div>
        </div>
      </div>
    </div>
  );
}

export default AdminPanel;
