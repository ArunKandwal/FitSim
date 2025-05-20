# app.py
import streamlit as st #webpage
import plotly.graph_objects as go #to make graphs
from algorithms import first_fit, best_fit, worst_fit, next_fit, round_robin #contains algorithms
from models import MemoryBlock, Process #contains memory block and process classes
import time #for working with time

#Helper: Evaluate Best Algorithm
def evaluate_algorithms(processes, memory_blocks, algo_map):
    results = {}

    for name, algo in algo_map.items():
        mem_copy = [MemoryBlock(b.original_size) for b in memory_blocks]
        proc_copy = [Process(p.name, p.size) for p in processes]

        updated_blocks = algo(mem_copy, proc_copy)
        allocated = 0

        for p in proc_copy:
            if any(b.allocated_to == p.name for b in updated_blocks):
                allocated += 1

        results[name] = allocated

    best_algo = max(results, key=results.get)
    return best_algo, results

# Main Simulator
def simulate_realtime_graph(processes, memory_blocks, selected_algo, algo_label):
    st.subheader(f"📊 {algo_label} - Memory Usage & Allocation Visualization")

    # Side-by-side layout for graph + pie chart
    live_col, pie_col = st.columns([2, 1])
    chart_placeholder1 = live_col.empty()
    pie_placeholder = pie_col.empty()

    timer_placeholder = st.empty()
    progress_bar = st.progress(0)

    chart_layout = dict(
        xaxis_title="Step",
        yaxis_title="Usage (%)",
        yaxis_range=[0, 100],
        height=400,
        transition=dict(duration=500, easing="linear")
    )

    memory_fig = go.Figure()
    memory_fig.add_trace(go.Scatter(
        x=[], y=[],
        mode="lines+markers",
        line=dict(color="royalblue", width=2),
        marker=dict(size=6),
        name="Memory Usage"
    ))
    memory_fig.update_layout(title="📈 Memory Usage (%)", **chart_layout)

    allocated_processes = set()
    algo_start_time = time.time()

    for i, process in enumerate(processes):
        time.sleep(0.3)
        step_start_time = time.time()

        temp_blocks = [MemoryBlock(b.original_size) for b in memory_blocks]
        for j in range(len(memory_blocks)):
            temp_blocks[j].is_free = memory_blocks[j].is_free
            temp_blocks[j].allocated_to = memory_blocks[j].allocated_to
            temp_blocks[j].size = memory_blocks[j].size

        updated_blocks = selected_algo(temp_blocks, processes[:i+1])
        for k in range(len(memory_blocks)):
            memory_blocks[k].is_free = updated_blocks[k].is_free
            memory_blocks[k].allocated_to = updated_blocks[k].allocated_to
            memory_blocks[k].size = updated_blocks[k].size

        for p in processes[:i+1]:
            if any(b.allocated_to == p.name for b in memory_blocks):
                allocated_processes.add(p.name)

        used_memory = sum(b.original_size - b.size for b in memory_blocks)
        total_memory = sum(b.original_size for b in memory_blocks)
        memory_percent = round((used_memory / total_memory) * 100, 2)
        step_label = f"Step {i+1}"

        memory_fig.data[0].x += (step_label,)
        memory_fig.data[0].y += (memory_percent,)

        chart_placeholder1.plotly_chart(memory_fig, use_container_width=True)
        timer_placeholder.metric(label="Step Time (s)", value=round(time.time() - step_start_time, 2))
        progress_bar.progress((i + 1) / len(processes))

    # Final Pie Chart
    allocated = len(allocated_processes)
    failed = sum(1 for p in processes if p.name not in allocated_processes)
    pie_labels = ["Allocated", "Failed"]
    pie_values = [allocated, failed]

    pie_chart = go.Figure(
        data=[go.Pie(labels=pie_labels, values=pie_values, hole=0.4)],
        layout=go.Layout(
            title="📊 Allocation Status",
            height=400,
        )
    )
    pie_placeholder.plotly_chart(pie_chart, use_container_width=True)

    # Completion Message
    total_algo_time = round(time.time() - algo_start_time, 2)
    st.success(f"✅ {algo_label} Allocation Complete")
    st.metric(label="⏱️ Total Algorithm Execution Time", value=f"{total_algo_time} seconds")

    # Allocation Table
    st.subheader(f"📋 Final Allocation Table - {algo_label}")
    for i, block in enumerate(memory_blocks):
        status = "Free" if block.is_free else f"Allocated to {block.allocated_to}"
        st.markdown(f"- **Block {i+1}:** {block.size} KB remaining — {status}")

    # Memory Block Visualization
    st.subheader("🧱 Memory Block Visualization")
    bar_fig = go.Figure()

    labels, sizes, colors = [], [], []
    for block in memory_blocks:
        label = "Free" if block.is_free else block.allocated_to
        color = "lightgray" if block.is_free else "royalblue"
        size_used = block.original_size - block.size if not block.is_free else 0
        labels.append(label)
        sizes.append(size_used)
        colors.append(color)

    bar_fig.add_trace(go.Bar(
        x=sizes,
        y=["Memory"] * len(sizes),
        orientation="h",
        marker=dict(color=colors),
        text=labels,
        hoverinfo="text+x",
        width=0.3
    ))

    bar_fig.update_layout(
        height=100,
        xaxis_title="Memory Size",
        yaxis=dict(showticklabels=False),
        margin=dict(l=0, r=0, t=0, b=0)
    )

    st.plotly_chart(bar_fig, use_container_width=True, key=f"blockbar_{algo_label}")


# --- Streamlit UI ---
st.set_page_config(page_title="Memory Partitioning Simulator", layout="wide")
st.title("🧠 Memory Partitioning Simulator")

# Sidebar Input
with st.sidebar:
    st.header("⚙️ Configuration")
    memory_input = st.text_input("Enter Memory Block Sizes", "100,500,200,300,600")
    process_input = st.text_input("Enter Process Sizes", "212,417,112,426")

    algo_choice = st.radio(
        "Select Allocation Algorithm to Simulate",
        ["First Fit", "Best Fit", "Worst Fit", "Next Fit", "Round Robin"]
    )

    run_simulation = st.button("Run Allocation")

# Algorithm Map
algo_map = {
    "First Fit": first_fit,
    "Best Fit": best_fit,
    "Worst Fit": worst_fit,
    "Next Fit": next_fit,
    "Round Robin": round_robin
}

# Run Simulation
if run_simulation:
    try:
        memory_sizes = list(map(int, memory_input.split(',')))
        process_sizes = list(map(int, process_input.split(',')))
        processes = [Process(f"P{i+1}", size) for i, size in enumerate(process_sizes)]
        memory_blocks = [MemoryBlock(size) for size in memory_sizes]

        # Recommend best fit algorithm
        fit_algos = {k: v for k, v in algo_map.items() if k != "Round Robin"}
        recommended_algo, results = evaluate_algorithms(processes, memory_blocks, fit_algos)

        st.info(f"🏆 Best Algorithm for This Input: **{recommended_algo}** "
                f"({results[recommended_algo]} processes allocated)")

        simulate_realtime_graph(processes, memory_blocks, algo_map[algo_choice], algo_choice)

    except Exception as e:
        st.error(f"Error: {str(e)}")
