import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import random
import time
from threading import Thread

st.set_page_config(page_title="Quantum Sentinel", layout="wide", page_icon="🛡️")

# -----------------------------
# Simulation Parameters
# -----------------------------
NUM_NODES = 12
UPDATE_INTERVAL = 1.0  # seconds
PARTICLE_COUNT = 80

# -----------------------------
# Node Data Structure
# -----------------------------
class Node:
    def __init__(self, node_id):
        self.id = node_id
        self.status = "Healthy"  # Healthy, Compromised, Rogue
        self.temperature = random.randint(20, 40)
        self.battery = random.randint(50, 100)

    def update_sensors(self):
        if self.status == "Healthy":
            self.temperature += random.uniform(-0.5, 0.5)
            self.battery -= random.uniform(0, 0.5)
        elif self.status == "Compromised":
            self.temperature += random.uniform(0, 1)
            self.battery -= random.uniform(0.5, 1)
        elif self.status == "Rogue":
            self.temperature += random.uniform(1, 2)
            self.battery -= random.uniform(1, 2)
        self.temperature = max(min(self.temperature, 100), 0)
        self.battery = max(min(self.battery, 100), 0)

# -----------------------------
# Initialize Nodes and Graph
# -----------------------------
nodes = [Node(i) for i in range(NUM_NODES)]
G = nx.erdos_renyi_graph(NUM_NODES, 0.3, seed=42)

# -----------------------------
# Event Log
# -----------------------------
if 'event_log' not in st.session_state:
    st.session_state.event_log = []

def log_event(message):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.event_log.append(f"[{timestamp}] {message}")
    if len(st.session_state.event_log) > 50:
        st.session_state.event_log.pop(0)

# -----------------------------
# Simulation Thread
# -----------------------------
def update_nodes():
    while True:
        for node in nodes:
            node.update_sensors()
            if node.status == "Rogue":
                # Rogue can compromise neighbors
                neighbors = list(G.neighbors(node.id))
                for n in neighbors:
                    if nodes[n].status == "Healthy" and random.random() < 0.05:
                        nodes[n].status = "Compromised"
                        log_event(f"Node {n} compromised by Rogue Node {node.id}")
        time.sleep(UPDATE_INTERVAL)

thread = Thread(target=update_nodes, daemon=True)
thread.start()

# -----------------------------
# Streamlit Layout & CSS
# -----------------------------
st.markdown(
    """
    <style>
    .stApp { background-color: #0e1117; color: #ffffff; }
    .sidebar .sidebar-content { background-color: #111827; color: #ffffff; }
    .streamlit-expanderHeader { color: #ffffff; }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🛡️ Quantum Sentinel: Digital Twin Simulation")
col1, col2 = st.columns([2, 1])

# -----------------------------
# Sidebar Controls
# -----------------------------
with st.sidebar:
    st.header("Controls")
    if st.button("Inject Rogue Node"):
        healthy_nodes = [n for n in nodes if n.status == "Healthy"]
        if healthy_nodes:
            node = random.choice(healthy_nodes)
            node.status = "Rogue"
            log_event(f"Node {node.id} injected as Rogue")
        else:
            log_event("No Healthy node available to inject Rogue")

    if st.button("Heal Nodes"):
        compromised_nodes = [n for n in nodes if n.status == "Compromised"]
        for node in compromised_nodes:
            node.status = "Healthy"
            log_event(f"Node {node.id} healed to Healthy")

    if st.button("Detect Threats"):
        rogue_nodes = [n for n in nodes if n.status == "Rogue"]
        log_event(f"Detected Rogue Nodes: {[n.id for n in rogue_nodes]}")

    if st.button("Reset Network"):
        for node in nodes:
            node.status = "Healthy"
            node.temperature = random.randint(20, 40)
            node.battery = random.randint(50, 100)
        st.session_state.event_log = []
        log_event("Network Reset to Healthy State")

# -----------------------------
# Quantum Particle Background
# -----------------------------
def particle_background():
    particle_positions = [(random.random(), random.random()) for _ in range(PARTICLE_COUNT)]
    xs, ys = zip(*particle_positions)
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=xs, y=ys, mode='markers',
                             marker=dict(size=5, color='#00ffff', opacity=0.7)))
    fig.update_layout(xaxis=dict(visible=False), yaxis=dict(visible=False),
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      margin=dict(l=0, r=0, t=0, b=0), height=300)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Network Visualization with Tooltips
# -----------------------------
def plot_network_hover():
    color_map = {"Healthy": "#00FFAA", "Compromised": "#FFAA00", "Rogue": "#FF0055"}
    node_colors = [color_map[node.status] for node in nodes]
    hover_text = [f"Node {node.id}<br>Status: {node.status}<br>Temp: {node.temperature:.1f}°C<br>Battery: {node.battery:.1f}%" for node in nodes]
    pos = nx.spring_layout(G, seed=42)
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]
    edge_trace = go.Scatter(x=edge_x, y=edge_y, line=dict(width=1, color='#555555'), hoverinfo='none', mode='lines')
    
    node_x = [pos[node.id][0] for node in nodes]
    node_y = [pos[node.id][1] for node in nodes]

    node_trace = go.Scatter(
        x=node_x, y=node_y, mode='markers+text', hoverinfo='text', text=[str(n.id) for n in nodes],
        marker=dict(color=node_colors, size=30, line_width=2), textposition="top center", hovertext=hover_text
    )
    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(showlegend=False, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      xaxis=dict(showgrid=False, zeroline=False, visible=False),
                      yaxis=dict(showgrid=False, zeroline=False, visible=False), height=500)
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Display Main Panels
# -----------------------------
with col1:
    st.subheader("Quantum Particle Background")
    particle_background()

    st.subheader("Network Topology")
    plot_network_hover()

    # Analytics Charts
    st.subheader("Node Analytics")
    df = pd.DataFrame({
        "Node": [node.id for node in nodes],
        "Temperature": [node.temperature for node in nodes],
        "Battery": [node.battery for node in nodes],
        "Status": [node.status for node in nodes]
    })
    fig_temp = px.line(df, x="Node", y="Temperature", color="Status", title="Node Temperature", markers=True)
    fig_batt = px.line(df, x="Node", y="Battery", color="Status", title="Node Battery Level", markers=True)
    fig_status = px.pie(df, names="Status", title="Node Status Distribution")
    st.plotly_chart(fig_temp, use_container_width=True)
    st.plotly_chart(fig_batt, use_container_width=True)
    st.plotly_chart(fig_status, use_container_width=True)

with col2:
    st.subheader("Event Log")
    st.text_area("Logs", value="\n".join(st.session_state.event_log), height=700, key="logs")
