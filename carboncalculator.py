import streamlit as st
import matplotlib.pyplot as plt
from fpdf import FPDF
import io
import os
import tempfile
import time

# Carbon conversion factors
ELECTRICITY_CO2_FACTOR = 0.0005
NATURAL_GAS_CO2_FACTOR = 0.0053
FUEL_CO2_FACTOR = 2.32
WASTE_CO2_FACTOR = 0.57
TRAVEL_CO2_FACTOR = 2.31

# Title
st.title("Carbon Footprint Calculator")

# Company Name Section
company_name = st.text_input("Enter your company name:")

# Energy Usage Section
st.header("Energy Usage")
electricity_bill = st.number_input("What is your average monthly electricity bill (in euros)?", min_value=0.0, value=0.0)
natural_gas_bill = st.number_input("What is your average monthly natural gas bill (in euros)?", min_value=0.0, value=0.0)
fuel_bill = st.number_input("What is your average monthly fuel bill for transportation (in euros)?", min_value=0.0, value=0.0)

# Waste Section
st.header("Waste")
waste_per_month = st.number_input("How much waste do you generate per month (in kilograms)?", min_value=0.0, value=0.0)
recycling_percentage = st.number_input("What percentage of your waste is recycled or composted?", min_value=0.0, max_value=100.0, value=0.0)

# Business Travel Section
st.header("Business Travel")
km_per_year = st.number_input("How many kilometers do your employees travel per year for business purposes?", min_value=0.0, value=0.0)
fuel_efficiency = st.number_input("What is the average fuel efficiency of the vehicles used for business travel (liters per 100 kilometers)?", min_value=0.0, value=0.0)

# Carbon Footprint Calculation and PDF Generation Function
def calculate_emissions():
    # Carbon Footprint Calculations
    energy_emissions = (electricity_bill * 12 * ELECTRICITY_CO2_FACTOR) + (natural_gas_bill * 12 * NATURAL_GAS_CO2_FACTOR) + (fuel_bill * 12 * FUEL_CO2_FACTOR)
    waste_emissions = (waste_per_month * 12) * (WASTE_CO2_FACTOR - (recycling_percentage / 100))
    
    # Check for zero fuel efficiency to avoid division by zero error
    if fuel_efficiency > 0:
        travel_emissions = (km_per_year * (1 / fuel_efficiency)) * TRAVEL_CO2_FACTOR
    else:
        travel_emissions = 0

    # Total Emissions
    total_emissions = energy_emissions + waste_emissions + travel_emissions

    return total_emissions, energy_emissions, waste_emissions, travel_emissions

# Function to generate PDF with chart and save to a specific folder
def generate_pdf_with_chart(total_emissions, energy_emissions, waste_emissions, travel_emissions, company_name):
    pdf = FPDF()
    pdf.add_page()

    # Title
    pdf.set_font("Arial", style="B", size=16)
    pdf.set_text_color(0, 128, 0)  # Dark green for title
    pdf.cell(200, 10, txt=f"Carbon Footprint Report for {company_name}", ln=True, align="C")
    pdf.ln(10)

    # Body text
    pdf.set_font("Arial", size=12)
    pdf.set_text_color(0, 0, 0)  # Black for body
    pdf.cell(200, 10, txt=f"Total Carbon Footprint: {total_emissions:.2f} kgCO2/year", ln=True)
    pdf.cell(200, 10, txt=f"Energy Usage Emissions: {energy_emissions:.2f} kgCO2/year", ln=True)
    pdf.cell(200, 10, txt=f"Waste Emissions: {waste_emissions:.2f} kgCO2/year", ln=True)
    pdf.cell(200, 10, txt=f"Business Travel Emissions: {travel_emissions:.2f} kgCO2/year", ln=True)
    pdf.ln(10)

    # Bar chart
    categories = ["Energy Usage", "Waste", "Business Travel"]
    emissions = [energy_emissions, waste_emissions, travel_emissions]

    if any(emissions):
        # Plot the bar graph
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.bar(categories, emissions, color=['#2196F3', '#FF5722', '#9C27B0'])
        ax.set_title("Carbon Footprint Breakdown", fontsize=14, weight='bold', color="#4CAF50")
        ax.set_ylabel("Emissions (kgCO2/year)", fontsize=12)
        ax.set_xlabel("Categories", fontsize=12)
        plt.tight_layout()

        # Save the chart as a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp_chart_file:
            chart_path = tmp_chart_file.name
            plt.savefig(chart_path, dpi=300)
            plt.close(fig)  # Close the figure to free resources

            # Embed chart into PDF
            pdf.image(chart_path, x=10, y=pdf.get_y(), w=180)

            # Explicit cleanup: Introduce a short delay before attempting to delete the file
            time.sleep(1)  # Adding a slight delay to ensure the file is not being used
            try:
                os.remove(chart_path)  # Delete the temporary chart file after embedding it
            except PermissionError:
                print(f"Could not delete the file {chart_path}. It may still be in use.")
    else:
        pdf.cell(200, 10, txt="No emissions data available for chart.", ln=True)

    # Footer
    pdf.set_y(-20)
    pdf.set_font("Arial", size=10)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(0, 10, txt="Thank you for using the Carbon Footprint Calculator.", ln=True, align="C")

    # Create a temporary PDF file to return
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_pdf_file:
        pdf.output(tmp_pdf_file.name)  # Save PDF to the temporary file
        tmp_pdf_path = tmp_pdf_file.name  # Get the path to the temp file

    return tmp_pdf_path  # Return the path to the saved PDF

# Streamlit UI for inputs and download button
if st.button("Calculate Carbon Footprint"):
    total_emissions, energy_emissions, waste_emissions, travel_emissions = calculate_emissions()
    
    # Generate PDF and save it to the specified folder
    pdf_file_path = generate_pdf_with_chart(total_emissions, energy_emissions, waste_emissions, travel_emissions, company_name)

    # Provide a download button for the generated PDF
    with open(pdf_file_path, "rb") as pdf_file:
        st.download_button(
            label="Download PDF Report",
            data=pdf_file.read(),  # Read file content as binary
            file_name=f"{company_name}_carbon_footprint_report.pdf",
            mime="application/pdf"
        )

    # Optionally clean up temporary file after download (uncomment if needed)
    # os.remove(pdf_file_path)
