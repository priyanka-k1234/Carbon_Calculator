import matplotlib.pyplot as plt

def plot_charts(energy: float, waste: float, travel: float):
    """
    Create a pie chart showing the carbon footprint breakdown with a legend.

    Args:
        energy (float): Energy-related footprint.
        waste (float): Waste-related footprint.
        travel (float): Travel-related footprint.

    Returns:
        fig (matplotlib.figure.Figure): The figure object.
        ax (matplotlib.axes.Axes): The axes object.
    """
    # Labels and sizes for the pie chart
    labels = ['Energy', 'Waste', 'Travel']
    sizes = [energy, waste, travel]
    colors = ['#ff9999', '#66b3ff', '#99ff99']  # Custom colors for each category
    explode = (0.1, 0, 0)  # "Explode" the first slice (Energy) for emphasis

    # Create the pie chart
    fig, ax = plt.subplots(figsize=(8, 6))
    wedges, texts, autotexts = ax.pie(
        sizes,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',  # Show percentages on the chart
        startangle=140,  # Rotate the chart for better readability
        shadow=True,  # Add a shadow effect
        textprops={'color': 'black'}  # Set text color
    )

    # Add a legend
    ax.legend(wedges, labels, loc="upper right", fontsize=12)

    # Add a title
    ax.set_title('Carbon Footprint Breakdown', fontsize=16, color='black')

    return fig, ax