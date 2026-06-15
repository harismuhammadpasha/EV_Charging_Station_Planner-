"""Streamlit frontend for the EV Charging Station Planner."""
import time
import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt

plt.rcParams['figure.facecolor'] = '#0E1117'
plt.rcParams['savefig.facecolor'] = '#0E1117'

from config import CITY_EDGES, CHARGING_STATIONS, KWH_PER_KM, CHARGING_COST_PER_KWH
from models import Vehicle, ChargingStation
from route_planner import RoutePlanner


@st.cache_resource
def build_graph():
    graph = nx.Graph()
    for u, v, w in CITY_EDGES:
        graph.add_edge(u, v, weight=w)
    return graph


def get_positions():
    """Approximate geographic layout (longitude, latitude-like) for Punjab cities."""
    return {
        'RAWALPINDI':    (0.5, 10),
        'ISLAMABAD':     (0.8, 10.3),
        'HARIPUR':       (0.3, 11),
        'JHELUM':        (1.5, 8.8),
        'GUJRAT':        (2.2, 8.2),
        'SARGODHA':      (1.0, 7.0),
        'GUJRANWALA':    (2.6, 7.2),
        'SIALKOT':       (3.2, 7.8),
        'SHEIKHUPURA':   (2.8, 6.2),
        'LAHORE':        (3.4, 5.5),
        'FAISALABAD':    (1.6, 5.5),
        'JHANG':         (0.8, 5.8),
        'SHORKOT':       (0.6, 4.8),
        'TOBATEKSINGH':  (1.8, 4.5),
        'OKARA':         (2.8, 4.0),
        'SAHIWAL':       (2.2, 3.2),
        'KHANEWAL':      (1.6, 2.4),
        'MULTAN':        (1.0, 1.8),
        'BAHAWALPUR':    (1.8, 0.8),
    }


def style_dark_graph(fig, ax):
    fig.patch.set_facecolor('#0E1117')
    ax.set_facecolor('#0E1117')
    ax.title.set_color('#FAFAFA')


def draw_route(graph, pos, path, charging_stations, start, end, distance):
    path_edges = list(zip(path, path[1:]))

    def is_path_edge(u, v):
        return (u, v) in path_edges or (v, u) in path_edges

    node_colors = ['#00FF7F' if n in charging_stations else '#00D9FF' for n in graph.nodes()]
    edge_colors = ['#FF4B4B' if is_path_edge(u, v) else '#444444' for u, v in graph.edges()]
    edge_widths = [3.5 if is_path_edge(u, v) else 1 for u, v in graph.edges()]

    fig, ax = plt.subplots(figsize=(10, 11))
    style_dark_graph(fig, ax)
    nx.draw(graph, pos, with_labels=True, node_color=node_colors, node_size=900,
            font_size=10, font_color='white', font_weight='bold',
            edge_color=edge_colors, width=edge_widths, ax=ax)
    labels = nx.get_edge_attributes(graph, 'weight')
    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=8,
                                  font_color='#CCCCCC', ax=ax)
    ax.set_title(f"{start} -> {end}  |  Distance: {distance} km", fontsize=13, fontweight='bold')
    return fig


def animate_route(graph, pos, path, charging_stations, start, end, distance):
    placeholder = st.empty()
    progress_text = st.empty()

    node_colors = ['#00FF7F' if n in charging_stations else '#00D9FF' for n in graph.nodes()]
    labels = nx.get_edge_attributes(graph, 'weight')

    for step in range(1, len(path) + 1):
        revealed_path = path[:step]
        path_edges = list(zip(revealed_path, revealed_path[1:]))

        def is_path_edge(u, v):
            return (u, v) in path_edges or (v, u) in path_edges

        edge_colors = ['#FF4B4B' if is_path_edge(u, v) else '#333333' for u, v in graph.edges()]
        edge_widths = [3.5 if is_path_edge(u, v) else 1 for u, v in graph.edges()]
        node_sizes = [1400 if n in revealed_path else 1000 for n in graph.nodes()]

        fig, ax = plt.subplots(figsize=(10, 11))
        style_dark_graph(fig, ax)
        nx.draw(graph, pos, with_labels=False, node_color=node_colors, node_size=node_sizes,
                edge_color=edge_colors, width=edge_widths, ax=ax)

        for node, (x, y) in pos.items():
            ax.text(x, y, node, fontsize=7, fontweight='bold', color='black',
                    ha='center', va='center', zorder=5)

        nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=8,
                                      font_color='#CCCCCC', ax=ax)

        current_city = revealed_path[-1]
        ax.set_title(f"Building Route: {start} -> {end}", fontsize=13, fontweight='bold')

        placeholder.pyplot(fig)
        plt.close(fig)

        progress_text.markdown(f"**Step {step}/{len(path)}:** Reached `{current_city}`")
        time.sleep(1.0)

    progress_text.markdown(f"✅ **Route complete!** Total distance: {distance} km")

    # Final frame
    fig, ax = plt.subplots(figsize=(10, 11))
    style_dark_graph(fig, ax)
    path_edges = list(zip(path, path[1:]))

    def is_final_edge(u, v):
        return (u, v) in path_edges or (v, u) in path_edges

    edge_colors = ['#FF4B4B' if is_final_edge(u, v) else '#333333' for u, v in graph.edges()]
    edge_widths = [3.5 if is_final_edge(u, v) else 1 for u, v in graph.edges()]
    node_sizes = [1400 if n in path else 1000 for n in graph.nodes()]

    nx.draw(graph, pos, with_labels=False, node_color=node_colors, node_size=node_sizes,
            edge_color=edge_colors, width=edge_widths, ax=ax)

    for node, (x, y) in pos.items():
        ax.text(x, y, node, fontsize=7, fontweight='bold', color='black',
                ha='center', va='center', zorder=5)

    nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=8,
                                  font_color='#CCCCCC', ax=ax)
    ax.set_title(f"{start} -> {end}  |  Distance: {distance} km", fontsize=13, fontweight='bold')
    placeholder.pyplot(fig)
    plt.close(fig)


def metric_card(label, value, color="#00D9FF"):
    st.markdown(
        f"""
        <div style="
            background-color:#1A1F2C;
            border-left: 5px solid {color};
            border-radius: 10px;
            padding: 16px 20px;
            margin-bottom: 10px;
        ">
            <div style="color:#9AA0AC; font-size:13px; text-transform:uppercase; letter-spacing:1px;">{label}</div>
            <div style="color:#FAFAFA; font-size:26px; font-weight:700; margin-top:4px;">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main():
    st.set_page_config(page_title="EV Charging Station Planner", layout="wide", page_icon="⚡")

    st.markdown(
        """
        <h1 style="margin-bottom:0;">⚡ EV Charging Station Planner</h1>
        <p style="color:#9AA0AC; margin-top:4px;">
        Dijkstra Shortest Path &nbsp;|&nbsp; Greedy Battery-Aware Charging &nbsp;|&nbsp; Prim's MST
        </p>
        <hr style="border-color:#2A2F3C;">
        """,
        unsafe_allow_html=True,
    )

    graph = build_graph()
    pos = get_positions()
    stations_dict = {name: ChargingStation(name=name, cost_per_kwh=CHARGING_COST_PER_KWH)
                      for name in CHARGING_STATIONS}
    planner = RoutePlanner(graph, stations_dict)

    cities = sorted(graph.nodes)

    with st.sidebar:
        st.markdown("### 🛣️ Route Settings")
        start = st.selectbox("Start City", cities, index=cities.index("RAWALPINDI") if "RAWALPINDI" in cities else 0)
        end = st.selectbox("Destination City", cities, index=cities.index("SAHIWAL") if "SAHIWAL" in cities else len(cities) - 1)
        battery = st.number_input("Battery Range (km)", min_value=50, max_value=600, value=150, step=10)
        plan_clicked = st.button("🔍 Plan Route", type="primary", use_container_width=True)

        st.markdown("---")
        show_mst = st.checkbox("🌐 Show Minimum Spanning Network (Prim's)")

    if plan_clicked:
        vehicle = Vehicle(name="My EV", battery_capacity_km=float(battery), kwh_per_km=KWH_PER_KM)

        plain_dist, plain_path = planner.shortest_path(start, end)
        result = planner.ev_aware_route(start, end, vehicle)

        if not result.is_feasible:
            st.error("⚠️ No feasible path found within this battery range!")
            return

        battery_pct = (result.final_battery_km / vehicle.battery_capacity_km) * 100
        cost = planner.estimate_charging_cost(result, vehicle) if result.charging_stops else 0

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            metric_card("Total Distance", f"{result.distance_km} km")
        with col2:
            metric_card("Battery at Arrival", f"{result.final_battery_km} km ({battery_pct:.0f}%)",
                         color="#FF4B4B" if battery_pct < 20 else "#00FF7F")
        with col3:
            metric_card("Charging Stops", f"{len(result.charging_stops)}")
        with col4:
            metric_card("Charging Cost", f"Rs. {cost:.0f}")

        st.markdown("### 🗺️ Route Map")
        animate_route(graph, pos, result.path, set(CHARGING_STATIONS), start, end, result.distance_km)

        c1, c2 = st.columns(2)
        with c1:
            st.markdown("#### 📍 EV-Aware Path")
            st.code(" -> ".join(result.path))
            if result.charging_stops:
                st.write(f"**Charging Stops:** {', '.join(result.charging_stops)}")
            else:
                st.write("**Charging Stops:** None needed")

        with c2:
            st.markdown("#### 📍 Normal Dijkstra Path (no battery limit)")
            st.code(" -> ".join(plain_path))
            st.write(f"**Distance:** {plain_dist} km")

            if result.distance_km > plain_dist:
                st.info(f"EV path is **{result.distance_km - plain_dist} km longer** due to battery constraints.")
            else:
                st.success("EV path matches the shortest route — no detour needed.")

        if battery_pct < 20:
            st.warning("⚠️ Battery is low at arrival! Consider an extra charging stop.")

    else:
        st.info("👈 Select start/destination city and battery range from the sidebar, then click **Plan Route**.")

    if show_mst:
        st.markdown("---")
        st.markdown("### 🌐 Minimum Spanning Network (Prim's Algorithm)")
        mst, total_cost = planner.minimum_spanning_network()

        metric_card("Total Network Cost", f"{total_cost} km", color="#9D4EDD")

        fig, ax = plt.subplots(figsize=(10, 11))
        style_dark_graph(fig, ax)
        node_colors = ['#00FF7F' if n in CHARGING_STATIONS else '#00D9FF' for n in graph.nodes()]
        nx.draw(graph, pos, with_labels=False, node_color=node_colors, node_size=900,
                edge_color='#333333', width=1, ax=ax)

        for node, (x, y) in pos.items():
            ax.text(x, y, node, fontsize=7, fontweight='bold', color='black',
                    ha='center', va='center', zorder=5)

        nx.draw_networkx_edges(mst, pos, edge_color='#9D4EDD', width=3.5, ax=ax)
        labels = nx.get_edge_attributes(graph, 'weight')
        nx.draw_networkx_edge_labels(graph, pos, edge_labels=labels, font_size=8,
                                      font_color='#CCCCCC', ax=ax)
        ax.set_title("Minimum Spanning Network (Prim's Algorithm)", fontsize=13, fontweight='bold')
        st.pyplot(fig)


if __name__ == "__main__":
    main()