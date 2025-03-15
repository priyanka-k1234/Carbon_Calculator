from fpdf import FPDF

def generate_pdf(user_id, electricity, gas, fuel, waste, recycling, travel, efficiency, total_footprint, energy_emissions, waste_emissions, travel_emissions, recommendations, file_path, image_path):
    pdf = FPDF()
    pdf.add_page()

    # Set font to Helvetica (default font)
    pdf.set_font("Helvetica", size=16)

    # Add title
    pdf.cell(200, 10, txt="Carbon Footprint Report", ln=True, align='C')

    # Add user information
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt=f"User ID: {user_id}", ln=True, align='L')

    # Add inputs
    pdf.cell(200, 10, txt=f"Monthly Electricity Bill (EUR): {electricity}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Monthly Natural Gas Bill (EUR): {gas}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Monthly Fuel Bill (EUR): {fuel}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Waste Generated (kg): {waste}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Recycling Percentage (%): {recycling * 100}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Business Travel (km): {travel}", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Fuel Efficiency (L/100km): {efficiency}", ln=True, align='L')

    # Add total footprint
    pdf.cell(200, 10, txt=f"Total Carbon Footprint: {total_footprint:.2f} kgCO2", ln=True, align='L')

    # Add emissions breakdown
    pdf.cell(200, 10, txt=f"Energy Emissions: {energy_emissions:.2f} kgCO2", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Waste Emissions: {waste_emissions:.2f} kgCO2", ln=True, align='L')
    pdf.cell(200, 10, txt=f"Travel Emissions: {travel_emissions:.2f} kgCO2", ln=True, align='L')

    # Add recommendations
    pdf.cell(200, 10, txt="Recommendations:", ln=True, align='L')
    for recommendation in recommendations:
        # Replace unsupported characters (e.g., "€" with "EUR")
        recommendation = recommendation.replace("€", "EUR")
        pdf.cell(200, 10, txt=recommendation, ln=True, align='L')

    # Add graph image
    pdf.image(image_path, x=10, y=150, w=180)

    # Save the PDF
    pdf.output(file_path)