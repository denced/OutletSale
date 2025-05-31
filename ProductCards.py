import pandas as pd
import os
from PIL import Image

# Skip the first row ("Table 1") when reading the CSV file
data = pd.read_csv('MDList.csv', skiprows=1)

# Print the first few rows of the CSV file for debugging
print("First few rows of the CSV file:")
print(data.head())

# Normalize column names to avoid case or whitespace issues
data.columns = data.columns.str.strip().str.lower()

# Print normalized column names for debugging
print("Normalized column names:", data.columns.tolist())

# Filter out items with Woodbury column value as "0"
data = data[data['woodbury'] != 0]

# Group items by unique itemcolorkey and consolidate sizes
grouped_data = data.groupby('itemcolorkey').agg({
    'itemmodel': 'first',
    'outletfullprice': 'first',
    'discount': 'first',
    'finaloutletprice': 'first',
    'size': lambda x: ', '.join(sorted(set(s.strip() for s in ','.join(x).split(','))))
}).reset_index()

# Folder containing images
image_folder = 'images'

# Load the pricing.csv file to get colorName information
pricing_data = pd.read_csv('pricing.csv')
pricing_data.columns = pricing_data.columns.str.strip().str.lower()

# Clean and convert the retailFP column to numeric format
pricing_data['retailfp'] = pricing_data['retailfp'].replace(r'[\$,]', '', regex=True).astype(float)

# Update the function to use the corrected column name
def get_color_name(color_key):
    matching_row = pricing_data[pricing_data['itemcolorkey'].str[-3:] == color_key]
    if not matching_row.empty:
        return matching_row.iloc[0]['color']
    return None

# Ensure the retail price is properly parsed and returned as a numeric value
def get_retail_price(item_color_key):
    matching_row = pricing_data[pricing_data['itemcolorkey'] == item_color_key]
    if not matching_row.empty:
        return matching_row.iloc[0]['retailfp']
    return None

# Function to generate product cards
def generate_product_cards(grouped_data, image_folder):
    product_cards = []

    for _, row in grouped_data.iterrows():
        item_color_key = str(row['itemcolorkey'])  # Use normalized column name
        item_model = row['itemmodel']  # Use normalized column name
        outlet_full_price = row['outletfullprice']  # Use normalized column name
        discount = row['discount']  # Use normalized column name
        final_outlet_price = row['finaloutletprice']  # Use normalized column name

        # Extract itemCode and colorKey
        item_code = item_color_key[:10]
        color_key = item_color_key[10:13]

        # Find the image prioritizing 13-digit ItemColorKey
        image_name = f"{item_color_key}.jpg"
        if not os.path.exists(os.path.join(image_folder, image_name)):
            # Fall back to PNG format
            image_name = f"{item_color_key}.png"
        if not os.path.exists(os.path.join(image_folder, image_name)):
            # Fall back to 10-digit item code in JPG format
            image_name = f"{item_code}.jpg"
        if not os.path.exists(os.path.join(image_folder, image_name)):
            # Fall back to 10-digit item code in PNG format
            image_name = f"{item_code}.png"

        # Check if the image exists
        if not os.path.exists(os.path.join(image_folder, image_name)):
            image_name = None  # No image available

        # Update image URL to use the corrected GitHub Pages location
        if image_name:
            image_url = f"https://media.githubusercontent.com/media/denced/OutletSale/main/images/{image_name}"
        else:
            image_url = "https://media.githubusercontent.com/media/denced/OutletSale/main/images/placeholder.jpg"

        # Get the colorName
        color_name = get_color_name(color_key)

        # Get consolidated sizes
        sizes_text = row['size']
        if sizes_text.lower() == 'unknown':
            sizes_text = None

        # Get the retail price
        retail_price = get_retail_price(item_color_key)

        # Use the image URL in the product card
        product_card = f"""
        <div class="product-card">
        <img src='{image_url}' alt='Product Image' />
        <p>{item_model}</p>
        <p>{item_code} - {color_key}</p>
        """
        if color_name:
            product_card += f"<p>Color: {color_name}</p>"
        if sizes_text:
            product_card += f"<p>Sizes Available: {sizes_text}</p>"
        if retail_price:
            product_card += f"<p>Retail Price: {retail_price}</p>"
        product_card += f"<p>Outlet Price: {outlet_full_price}</p>"
        product_card += f"""
            <p>- {discount}</p>
            <p>Memorial Day Sale Price: {final_outlet_price}</p>
        </div>
        """
        product_cards.append(product_card)

    return product_cards

# Generate product cards
product_cards = generate_product_cards(grouped_data, image_folder)

# Update the file name to 'index.html'
with open('index.html', 'w') as f:
    f.write("<html><head><style>")
    f.write(".product-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 16px; } ")
    f.write(".product-card { border: 1px solid #ccc; padding: 16px; text-align: left; padding-left: 20px; font-family: 'Arial', sans-serif; font-size: 12px; line-height: 1.6; } ")
    f.write(".product-card img { max-width: 100%; height: auto; margin-bottom: 10px; }")
    f.write("</style></head><body>")
    f.write("<div class='product-grid'>")
    f.write("\n".join(product_cards))
    f.write("</div></body></html>")

# Update the print statement to reflect the new file name
print("Product cards generated and saved to index.html")