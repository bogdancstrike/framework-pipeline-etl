import React, {useState, useCallback, useEffect} from 'react';
import ReactFlow, {
    ReactFlowProvider,
    addEdge,
    MiniMap,
    Controls,
    Background,
    Handle,
    useNodesState,
    useEdgesState,
    getSmoothStepPath,
} from 'react-flow-renderer';
import dagre from 'dagre';
import {Button, Input, Slider, notification, Modal} from 'antd';
import {InfoCircleFilled} from '@ant-design/icons';
import './App.css';
import {fetchConsumerConfigs, updateConsumerConfigs} from './network';  // Import the API methods

// Layout using Dagre
const getLayoutedElements = (nodes, edges, direction = 'LR', ranksep = 200, nodesep = 200) => {
    const dagreGraph = new dagre.graphlib.Graph();
    dagreGraph.setDefaultEdgeLabel(() => ({}));
    const isHorizontal = direction === 'LR';
    dagreGraph.setGraph({
        rankdir: direction,
        ranksep: ranksep, // Adjusted space between nodes vertically
        nodesep: nodesep, // Adjusted space between nodes horizontally
    });

    nodes.forEach((node) => {
        dagreGraph.setNode(node.id, {width: 172, height: 36});
    });

    edges.forEach((edge) => {
        dagreGraph.setEdge(edge.source, edge.target);
    });

    dagre.layout(dagreGraph);

    nodes.forEach((node) => {
        const nodeWithPosition = dagreGraph.node(node.id);
        node.targetPosition = isHorizontal ? 'left' : 'top';
        node.sourcePosition = isHorizontal ? 'right' : 'bottom';

        node.position = {
            x: nodeWithPosition.x - 172 / 2,
            y: nodeWithPosition.y - 36 / 2,
        };

        return node;
    });

    return {nodes, edges};
};

// Custom Node for Workers with Editable Name and Delete Button
const WorkerNode = ({data, id}) => {
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [metadata, setMetadata] = useState(data.metadata || '');
    const [kafkaBootstrapServer, setKafkaBootstrapServer] = useState(data.kafkaBootstrapServer || 'localhost:9092');
    const [timeout, setTimeoutValue] = useState(data.timeout !== undefined ? data.timeout : null);

    const onDeleteClick = () => {
        data.onDeleteNode(id);
    };

    const handleModalOk = () => {
        Modal.confirm({
            title: 'Are you sure you want to save these changes?',
            onOk: () => {
                data.onMetadataChange(id, metadata);
                data.onKafkaBootstrapServerChange(id, kafkaBootstrapServer);
                data.onTimeoutChange(id, timeout);
                setIsModalOpen(false);
            },
        });
    };

    return (
        <div
            style={{
                backgroundColor: '#FFC0CB',
                padding: '10px',
                borderRadius: '5px',
                border: '1px solid #000',
                position: 'relative',
            }}
        >
            <Handle type="target" position="left" style={{background: '#555'}}/>
            <Input
                value={data.label}
                onChange={(e) => data.onLabelChange(id, e.target.value)}
                style={{width: '100%', marginBottom: '5px', fontWeight: 'bold'}}
            />
            <div
                style={{
                    position: 'absolute',
                    top: '5px',
                    right: '5px',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                }}
            >
                <InfoCircleFilled
                    onClick={() => setIsModalOpen(true)}
                    style={{
                        cursor: 'pointer',
                        fontSize: '20px',
                        color: '#1890ff',
                        // backgroundColor: 'white',
                        // borderRadius: '50%',
                        padding: '3px'
                    }}
                />
                <button
                    onClick={onDeleteClick}
                    style={{
                        background: 'red',
                        color: 'white',
                        border: 'none',
                        borderRadius: '50%',
                        width: '20px',
                        height: '20px',
                        cursor: 'pointer',
                    }}
                >
                    &times;
                </button>
            </div>
            <Handle type="source" position="right" style={{background: '#555'}}/>
            <Modal
                title="Editing..."
                visible={isModalOpen}
                onOk={handleModalOk}
                onCancel={() => setIsModalOpen(false)}
            >
                <p>Metadata</p>
                <Input.TextArea
                    value={metadata}
                    onChange={(e) => setMetadata(e.target.value)}
                    rows={4}
                    placeholder="Enter metadata here"
                />

                <p>Kafka Bootstrap Server</p>
                <Input
                    value={kafkaBootstrapServer}
                    onChange={(e) => setKafkaBootstrapServer(e.target.value)}
                    style={{marginTop: '10px'}}
                    placeholder="Kafka Bootstrap Server"
                />

                <p>Timeout</p>
                <Input
                    type="number"
                    value={timeout !== null ? timeout : ''}
                    onChange={(e) => setTimeoutValue(e.target.value !== '' ? Number(e.target.value) : null)}
                    style={{marginTop: '10px'}}
                    placeholder="Timeout (seconds)"
                />
            </Modal>
        </div>
    );
};

// Custom Node for Topics with Editable Name and Delete Button
const TopicNode = ({data, id}) => {
    const onDeleteClick = () => {
        data.onDeleteNode(id);
    };

    const onChange = (e) => {
        data.onLabelChange(id, e.target.value);
    };

    return (
        <div
            style={{
                backgroundColor: '#ADD8E6',
                padding: '10px',
                borderRadius: '5px',
                border: '1px solid #000',
                position: 'relative',
            }}
        >
            <Handle type="target" position="left" style={{background: '#555'}}/>
            <Input
                value={data.label}
                onChange={onChange}
                style={{width: '100%', marginBottom: '5px', fontWeight: 'bold'}}
            />
            <button
                onClick={onDeleteClick}
                style={{
                    position: 'absolute',
                    top: '5px',
                    right: '5px',
                    background: 'red',
                    color: 'white',
                    border: 'none',
                    borderRadius: '50%',
                    width: '20px',
                    height: '20px',
                    cursor: 'pointer',
                }}
            >
                &times;
            </button>
            <Handle type="source" position="right" style={{background: '#555'}}/>
        </div>
    );
};

// Custom Edge with Delete Button using SmoothStep
const CustomSmoothStepEdge = ({
                                  id,
                                  sourceX,
                                  sourceY,
                                  targetX,
                                  targetY,
                                  sourcePosition,
                                  targetPosition,
                                  style,
                                  markerEnd,
                                  data,
                              }) => {
    const [edgePath] = getSmoothStepPath({
        sourceX,
        sourceY,
        sourcePosition,
        targetX,
        targetY,
        targetPosition,
    });

    const onEdgeClick = (evt, edgeId) => {
        evt.stopPropagation();
        data.onEdgeDelete(edgeId);
    };

    return (
        <>
            <path
                id={id}
                style={style}
                className="react-flow__edge-path"
                d={edgePath}
                markerEnd={markerEnd}
            />
            <text>
                <textPath
                    href={`#${id}`}
                    style={{fontSize: 12}}
                    startOffset="50%"
                    textAnchor="middle"
                >
                    <tspan
                        dy={-10}
                        xlinkHref={`#${id}`}
                        className="delete-btn"
                        onClick={(evt) => onEdgeClick(evt, id)}
                    >
                        Delete
                    </tspan>
                </textPath>
            </text>
        </>
    );
};

// Custom Edge with Delete Button using Floating
const CustomFloatingEdge = ({
                                id,
                                sourceX,
                                sourceY,
                                targetX,
                                targetY,
                                sourcePosition,
                                targetPosition,
                                style,
                                markerEnd,
                                data,
                            }) => {
    const path = `M${sourceX},${sourceY} C${sourceX + (targetX - sourceX) / 2},${sourceY} ${targetX - (targetX - sourceX) / 2},${targetY} ${targetX},${targetY}`;

    const onEdgeClick = (evt, edgeId) => {
        evt.stopPropagation();
        data.onEdgeDelete(edgeId);
    };

    return (
        <>
            <path
                id={id}
                style={style}
                className="react-flow__edge-path"
                d={path}
                markerEnd={markerEnd}
            />
            <text>
                <textPath
                    href={`#${id}`}
                    style={{fontSize: 12}}
                    startOffset="50%"
                    textAnchor="middle"
                >
                    <tspan
                        dy={-10}
                        xlinkHref={`#${id}`}
                        className="delete-btn"
                        onClick={(evt) => onEdgeClick(evt, id)}
                    >
                        Delete
                    </tspan>
                </textPath>
            </text>
        </>
    );
};

// Define nodeTypes and edgeTypes here
const nodeTypes = {
    worker: WorkerNode,
    topic: TopicNode,
};

const edgeTypes = {
    smoothstep: CustomSmoothStepEdge,
    customEdge: CustomFloatingEdge,
};

const FlowApp = () => {
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);
    const [nodeIdCounter, setNodeIdCounter] = useState(1);  // Start with 1
    const [edgeType, setEdgeType] = useState('customEdge'); // Default edge type
    const [ranksep, setRanksep] = useState(200);
    const [nodesep, setNodesep] = useState(200);

    const openNotification = () => {
        notification.success({
            message: 'Graph Saved',
            description: 'The graph was successfully saved!',
        });
    };

    const onDeleteNode = useCallback(
        (id) => {
            Modal.confirm({
                title: 'Are you sure you want to delete this node?',
                onOk: () => {
                    console.log(`Deleting node with id: ${id}`);
                    setNodes((nds) => nds.filter((node) => node.id !== id));
                    setEdges((eds) => eds.filter((edge) => edge.source !== id && edge.target !== id));
                },
            });
        },
        [setNodes, setEdges]
    );

    const onLabelChange = useCallback(
        (id, newLabel) => {
            setNodes((nds) =>
                nds.map((node) =>
                    node.id === id ? {...node, data: {...node.data, label: newLabel}} : node
                )
            );
        },
        [setNodes]
    );

    const onMetadataChange = useCallback(
        (id, newMetadata) => {
            setNodes((nds) =>
                nds.map((node) =>
                    node.id === id ? {...node, data: {...node.data, metadata: newMetadata}} : node
                )
            );
        },
        [setNodes]
    );

    const onKafkaBootstrapServerChange = useCallback(
        (id, newKafkaBootstrapServer) => {
            setNodes((nds) =>
                nds.map((node) =>
                    node.id === id
                        ? {...node, data: {...node.data, kafkaBootstrapServer: newKafkaBootstrapServer}}
                        : node
                )
            );
        },
        [setNodes]
    );

    const onTimeoutChange = useCallback(
        (id, newTimeout) => {
            setNodes((nds) =>
                nds.map((node) =>
                    node.id === id ? {...node, data: {...node.data, timeout: newTimeout}} : node
                )
            );
        },
        [setNodes]
    );

    const generateInitialNodesAndEdges = (data, onDeleteNode, onLabelChange, onMetadataChange, onKafkaBootstrapServerChange, onTimeoutChange) => {
        const nodes = [];
        const edges = [];
        const topics = new Set();

        data.forEach((item) => {
            nodes.push({
                id: `worker-${item.id}`,
                type: 'worker',
                data: {
                    label: item.consumer_name,
                    metadata: item.metadatas,
                    kafkaBootstrapServer: item.kafka_bootstrap_server,
                    timeout: item.timeout,
                    onDeleteNode,
                    onLabelChange,
                    onMetadataChange,
                    onKafkaBootstrapServerChange,
                    onTimeoutChange,
                },
                position: {x: 0, y: 0}, // Initial positions, will be updated by Dagre layout
            });

            if (item.topics_input) {
                item.topics_input.split(',').forEach((topic) => topics.add(topic));
            }
            if (item.topics_output) {
                item.topics_output.split(',').forEach((topic) => topics.add(topic));
            }

            if (item.topics_input) {
                item.topics_input.split(',').forEach((inputTopic) => {
                    edges.push({
                        id: `e-${inputTopic}-worker-${item.id}`,
                        source: inputTopic,
                        target: `worker-${item.id}`,
                        type: 'customEdge',
                        animated: true,
                    });
                });
            }

            if (item.topics_output) {
                item.topics_output.split(',').forEach((outputTopic) => {
                    edges.push({
                        id: `e-worker-${item.id}-${outputTopic}`,
                        source: `worker-${item.id}`,
                        target: outputTopic,
                        type: 'customEdge',
                        animated: true,
                    });
                });
            }
        });

        topics.forEach((topic) => {
            nodes.push({
                id: topic,
                type: 'topic',
                data: {label: topic, onDeleteNode, onLabelChange},
                position: {x: 0, y: 0}, // Initial positions, will be updated by Dagre layout
            });
        });

        return {nodes, edges};
    };

    useEffect(() => {
        const fetchData = async () => {
            try {
                const backendData = await fetchConsumerConfigs(); // Fetch data from the backend
                const {nodes, edges} = generateInitialNodesAndEdges(
                    backendData,
                    onDeleteNode,
                    onLabelChange,
                    onMetadataChange,
                    onKafkaBootstrapServerChange,
                    onTimeoutChange
                );
                const layouted = getLayoutedElements(nodes, edges, 'LR', ranksep, nodesep);
                setNodes(layouted.nodes);
                setEdges(layouted.edges);
                setNodeIdCounter(nodes.length + 1); // Update the node counter
            } catch (error) {
                console.error('Failed to fetch consumer configs:', error);
                notification.error({
                    message: 'Failed to Load Data',
                    description: 'An error occurred while fetching data from the server.',
                });
            }
        };

        fetchData();
    }, [setNodes, setEdges, ranksep, nodesep]);

    const onSave = async () => {
        Modal.confirm({
            title: 'Are you sure you want to save?',
            onOk: async () => {
                console.log('Current nodes:', nodes);
                console.log('Current edges:', edges);

                const tableStructure = nodes
                    .filter((node) => node.id.startsWith('worker'))
                    .map((worker) => {
                        const inputs = edges
                            .filter((edge) => edge.target === worker.id)
                            .map((edge) => nodes.find((node) => node.id === edge.source).data.label)
                            .join(',');

                        const outputs = edges
                            .filter((edge) => edge.source === worker.id)
                            .map((edge) => nodes.find((node) => node.id === edge.target).data.label)
                            .join(',');

                        return {
                            id: parseInt(worker.id.split('-')[1]),
                            worker_name: worker.data.label,
                            topics_input: inputs,
                            topics_output: outputs,
                            metadatas: worker.data.metadata,
                            kafka_bootstrap_server: worker.data.kafkaBootstrapServer,
                            timeout: worker.data.timeout,
                        };
                    });

                console.log('Generated Table Structure (JSON):', JSON.stringify(tableStructure, null, 2));

                try {
                    await updateConsumerConfigs(tableStructure); // Update data in the backend
                    openNotification();
                } catch (error) {
                    console.error('Failed to save consumer configs:', error);
                    notification.error({
                        message: 'Failed to Save Data',
                        description: 'An error occurred while saving data to the server.',
                    });
                }
            },
        });
    };

    const onAddWorker = useCallback(() => {
        const newWorker = {
            id: `worker-${nodeIdCounter}`,
            type: 'worker',
            data: {
                label: `Worker ${nodeIdCounter}`,
                onDeleteNode,
                onLabelChange,
                onMetadataChange,
                onKafkaBootstrapServerChange,
                onTimeoutChange,
            },
            position: {x: 200, y: Math.random() * 250},
        };

        setNodes((nds) => [...nds, newWorker]);
        setNodeIdCounter((id) => id + 1);
    }, [nodeIdCounter, setNodes]);

    const onAddTopic = useCallback(() => {
        const newTopic = {
            id: `topic-${nodeIdCounter}`,
            type: 'topic',
            data: {label: `Topic ${nodeIdCounter}`, onDeleteNode, onLabelChange},
            position: {x: 400, y: Math.random() * 250},
        };

        setNodes((nds) => [...nds, newTopic]);
        setNodeIdCounter((id) => id + 1);
    }, [nodeIdCounter, setNodes]);

    const onLayout = useCallback(
        (direction) => {
            const layouted = getLayoutedElements(nodes, edges, direction, ranksep, nodesep);
            setNodes([...layouted.nodes]);
            setEdges([...layouted.edges]);
        },
        [nodes, edges, ranksep, nodesep, setNodes, setEdges]
    );

    const toggleEdgeType = () => {
        const newEdgeType = edgeType === 'step' ? 'customEdge' : 'step';
        setEdgeType(newEdgeType);
        setEdges((eds) => eds.map((edge) => ({...edge, type: newEdgeType})));
    };

    const onConnect = useCallback(
        (params) =>
            setEdges((eds) =>
                addEdge({...params, type: edgeType, data: {onEdgeDelete}}, eds)
            ),
        [setEdges, edgeType]
    );

    const isValidConnection = (connection) => {
        const sourceNode = nodes.find((node) => node.id === connection.source);
        const targetNode = nodes.find((node) => node.id === connection.target);

        // Allow connections only between workers and topics
        return (
            (sourceNode.type === 'worker' && targetNode.type === 'topic') ||
            (sourceNode.type === 'topic' && targetNode.type === 'worker')
        );
    };

    const onEdgeDelete = useCallback(
        (id) => {
            Modal.confirm({
                title: 'Are you sure you want to delete this edge?',
                onOk: () => {
                    console.log(`Deleting edge with id: ${id}`);
                    setEdges((eds) => eds.filter((edge) => edge.id !== id));
                },
            });
        },
        [setEdges]
    );

    return (
        <div style={{height: '100vh'}}>
            <div className="controls">
                <Button type="primary" onClick={onAddWorker} style={{marginRight: 10}}>
                    Add Worker
                </Button>
                <Button type="primary" onClick={onAddTopic} style={{marginRight: 10}}>
                    Add Topic
                </Button>
                <Button type="default" onClick={() => onLayout('TB')} style={{marginRight: 10}}>
                    Vertical Layout
                </Button>
                <Button type="default" onClick={() => onLayout('LR')} style={{marginRight: 10}}>
                    Horizontal Layout
                </Button>
                <Button type="default" onClick={toggleEdgeType} style={{marginRight: 10}}>
                    Toggle Edge Type
                </Button>
                <Button
                    type="primary"
                    onClick={onSave}
                    style={{marginRight: 10, backgroundColor: 'green', borderColor: 'green'}}
                >
                    Save
                </Button>
            </div>
            <div style={{width: '200px', marginTop: '10px'}}>
                <label>Rank Separation: {ranksep}</label>
                <Slider
                    min={100}
                    max={500}
                    step={50}
                    value={ranksep}
                    onChange={(value) => setRanksep(value)}
                />
            </div>
            <div style={{width: '200px', marginTop: '10px'}}>
                <label>Node Separation: {nodesep}</label>
                <Slider
                    min={100}
                    max={500}
                    step={50}
                    value={nodesep}
                    onChange={(value) => setNodesep(value)}
                />
            </div>
            <ReactFlow
                nodes={nodes}
                edges={edges}
                onNodesChange={onNodesChange}
                onEdgesChange={onEdgesChange}
                onConnect={onConnect}
                nodeTypes={nodeTypes}
                edgeTypes={edgeTypes}
                fitView
                isValidConnection={isValidConnection}
                minZoom={0.1}
                maxZoom={5}
                defaultEdgeOptions={{data: {onEdgeDelete}}}
            >
                <MiniMap/>
                <Controls/>
                <Background/>
            </ReactFlow>
        </div>
    );
};

const App = () => (
    <ReactFlowProvider>
        <FlowApp/>
    </ReactFlowProvider>
);

export default App;
