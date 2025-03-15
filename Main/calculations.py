# calculations.py

# Import necessary modules
from config import CO2_PER_KWH, CO2_PER_GAS, CO2_PER_LITER_FUEL

def calculate_footprint(electricity: float, gas: float, fuel: float, waste: float, recycling: float, travel: float, efficiency: float) -> dict:
    """
    Calculate the total carbon footprint and its components.

    Args:
        electricity (float): Monthly electricity bill in €.
        gas (float): Monthly natural gas bill in €.
        fuel (float): Monthly fuel bill in €.
        waste (float): Waste generated in kg.
        recycling (float): Recycling percentage (0-100).
        travel (float): Business travel distance in km.
        efficiency (float): Fuel efficiency in L/100km.

    Returns:
        dict: A dictionary containing:
            - total_emissions (float): Total carbon footprint in kgCO2.
            - energy_emissions (float): Emissions from energy usage in kgCO2.
            - waste_emissions (float): Emissions from waste in kgCO2.
            - travel_emissions (float): Emissions from travel in kgCO2.

    Raises:
        ValueError: If any input is invalid.
    """
    # Validate inputs
    if efficiency <= 0:
        raise ValueError("Fuel efficiency must be greater than 0.")
    if recycling < 0 or recycling > 100:
        raise ValueError("Recycling percentage must be between 0 and 100.")

    # Calculate energy-related emissions
    energy_emissions = (electricity * 12 * CO2_PER_KWH) + (gas * 12 * CO2_PER_GAS) + (fuel * 12 * CO2_PER_LITER_FUEL)

    # Calculate waste-related emissions
    waste_emissions = waste * 12 * (0.57 - (recycling / 100))

    # Calculate travel-related emissions
    travel_emissions = travel * (1 / efficiency) * 2.31

    # Calculate total emissions
    total_emissions = energy_emissions + waste_emissions + travel_emissions

    return {
        "total_emissions": total_emissions,
        "energy_emissions": energy_emissions,
        "waste_emissions": waste_emissions,
        "travel_emissions": travel_emissions
    }

def calculate_offset(footprint: float) -> float:
    """
    Calculate the carbon offset required.

    Args:
        footprint (float): Total carbon footprint in kgCO2.

    Returns:
        float: Number of trees needed to offset the footprint.
    """
    return footprint / 21.77  # 1 tree offsets 21.77 kg of CO2 per year