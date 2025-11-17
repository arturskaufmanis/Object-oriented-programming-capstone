
"""
Shoe Inventory Management System
================================

This program provides a comprehensive system for managing 
a shoe inventory, with features
including adding new shoes, viewing inventory, searching, 
re-stocking, and calculating values.

Features:
    - Read and parse inventory data from a file
    - Add new shoe entries to the inventory
    - Display all shoes in a formatted table
    - Find and restock shoes with low quantity
    - Search for shoes by code
    - Calculate value of inventory items
    - Identify shoes with highest quantity

Requirements:
    - Python 3.6+
    - pandas library (for data manipulation)
    - tabulate library (for formatted table output)

References:
    - pandas documentation: https://pandas.pydata.org/docs/
    - tabulate documentation: https://pypi.org/project/tabulate/
    - Python file handling: https://docs.python.org/3/tutorial/inputoutput.html#reading-and-writing-files

Author: Arturs Kaufmanis. 
Date: May 10, 2025
"""

# Standard library imports
import os
import sys
import logging
from typing import List, Optional, Dict, Any

# Third-party imports
try:
    import pandas as pd
    from tabulate import tabulate
except ImportError as e:
    print(f"Error: Required library not found - {e}")
    print("Please install required libraries using: pip install pandas tabulate")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("inventory_system.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
INVENTORY_FILE = 'inventory.txt'
BACKUP_FILE = 'inventory_backup.txt'
DEFAULT_HEADER = "Country,Code,Product,Cost,Quantity"


class ShoeError(Exception):
    """Custom exception class for shoe-related errors"""
    pass


class Shoe:
    """
    A class to represent a shoe in the inventory.
    
    Attributes:
        country (str): Country of manufacture
        code (str): Unique product code
        product (str): Name of the product
        cost (float): Cost per unit
        quantity (int): Available quantity
    """
    
    def __init__(self, country: str, code: str, product: str, cost: str, quantity: str):
        """
        Initialize a Shoe object with the given attributes.
        
        Args:
            country (str): Country of manufacture
            code (str): Unique product code
            product (str): Name of the product
            cost (str): Cost per unit (will be converted to float)
            quantity (str): Available quantity (will be converted to int)
            
        Raises:
            ValueError: If cost is not a valid float or quantity is not a valid integer
        """
        self.country = country.strip()
        self.code = code.strip()
        self.product = product.strip()
        
        try:
            self.cost = float(cost)
            if self.cost < 0:
                raise ValueError("Cost cannot be negative")
        except ValueError as e:
            raise ValueError(f"Invalid cost value '{cost}': {str(e)}")
        
        try:
            self.quantity = int(quantity)
            if self.quantity < 0:
                raise ValueError("Quantity cannot be negative")
        except ValueError as e:
            raise ValueError(f"Invalid quantity value '{quantity}': {str(e)}")
    
    def get_cost(self) -> float:
        """Returns the cost of the shoes"""
        return self.cost
    
    def get_quantity(self) -> int:
        """Returns the quantity of the shoes"""
        return self.quantity
    
    def update_quantity(self, new_quantity: int) -> None:
        """
        Update the quantity of the shoe.
        
        Args:
            new_quantity (int): The new quantity value
            
        Raises:
            ValueError: If new_quantity is negative
        """
        if new_quantity < 0:
            raise ValueError("Quantity cannot be negative")
        self.quantity = new_quantity
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the shoe object to a dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the shoe
        """
        return {
            "Country": self.country,
            "Code": self.code,
            "Product": self.product,
            "Cost": self.cost,
            "Quantity": self.quantity,
            "Value": self.cost * self.quantity
        }
    
    def __str__(self) -> str:
        """Returns a string representation of the shoe object"""
        return (f"Country: {self.country}, Code: {self.code}, Product: {self.product}, "
                f"Cost: ${self.cost:.2f}, Quantity: {self.quantity}")


class InventoryManager:
    """
    A class to manage shoe inventory operations.
    
    Attributes:
        shoes_list (List[Shoe]): List to store shoe objects
        filename (str): Name of the inventory file
    """
    
    def __init__(self, filename: str = INVENTORY_FILE):
        """
        Initialize the InventoryManager with an empty list and specified filename.
        
        Args:
            filename (str, optional): Name of the inventory file. Defaults to INVENTORY_FILE.
        """
        self.shoes_list: List[Shoe] = []
        self.filename = filename
        self.header = DEFAULT_HEADER
    
    def read_shoes_data(self) -> bool:
        """
        Read shoe data from the inventory file and create shoe objects.
        
        Returns:
            bool: True if data was loaded successfully, False otherwise
        
        Raises:
            FileNotFoundError: If the inventory file is not found
            IOError: If there's an error reading the file
        """
        self.shoes_list = []  # Clear existing data
        
        try:
            if not os.path.exists(self.filename):
                logger.error(f"File not found: {self.filename}")
                return False
            
            with open(self.filename, 'r') as file:
                lines = file.readlines()
                
                if not lines:
                    logger.warning(f"File {self.filename} is empty")
                    return False
                
                # Store the header line
                self.header = lines[0].strip()
                
                # Process each line after the header
                line_number = 1
                for line in lines[1:]:
                    line_number += 1
                    line = line.strip()
                    if not line:  # Skip empty lines
                        continue
                    
                    parts = line.split(",")
                    if len(parts) != 5:
                        logger.warning(f"Line {line_number} has incorrect format: {line}")
                        continue
                    
                    try:
                        country, code, product, cost, quantity = parts
                        self.shoes_list.append(Shoe(country, code, product, cost, quantity))
                    except ValueError as e:
                        logger.error(f"Error on line {line_number}: {e}")
            
            if self.shoes_list:
                logger.info(f"Successfully loaded {len(self.shoes_list)} shoes from {self.filename}")
                return True
            else:
                logger.warning(f"No valid shoe entries found in {self.filename}")
                return False
                
        except FileNotFoundError:
            logger.error(f"Error: The file '{self.filename}' was not found")
            return False
        except IOError as e:
            logger.error(f"I/O error when reading file '{self.filename}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error reading from '{self.filename}': {e}")
            return False
    
    def save_shoes_data(self) -> bool:
        """
        Save all shoe data to the inventory file.
        
        Returns:
            bool: True if data was saved successfully, False otherwise
        """
        try:
            # Create a backup of the existing file if it exists
            if os.path.exists(self.filename):
                try:
                    with open(self.filename, 'r') as src, open(BACKUP_FILE, 'w') as dst:
                        dst.write(src.read())
                    logger.info(f"Created backup of {self.filename} to {BACKUP_FILE}")
                except IOError as e:
                    logger.warning(f"Could not create backup file: {e}")
            
            # Write the updated data
            with open(self.filename, 'w') as file:
                file.write(f"{self.header}\n")
                for shoe in self.shoes_list:
                    file.write(f"{shoe.country},{shoe.code},{shoe.product},{shoe.cost},{shoe.quantity}\n")
            
            logger.info(f"Successfully saved {len(self.shoes_list)} shoes to {self.filename}")
            return True
            
        except IOError as e:
            logger.error(f"I/O error when writing to file '{self.filename}': {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error saving to '{self.filename}': {e}")
            return False
    
    def capture_shoes(self) -> bool:
        """
        Capture data for a new shoe and add it to the inventory.
        
        Returns:
            bool: True if shoe was added successfully, False otherwise
        """
        try:
            print("\n=== Add New Shoe ===")
            country = input("Enter the country: ").strip()
            if not country:
                logger.warning("Country cannot be empty")
                print("Error: Country cannot be empty")
                return False
            
            code = input("Enter the code: ").strip()
            if not code:
                logger.warning("Code cannot be empty")
                print("Error: Code cannot be empty")
                return False
                
            # Check for duplicate codes
            if any(shoe.code.upper() == code.upper() for shoe in self.shoes_list):
                logger.warning(f"Shoe with code '{code}' already exists")
                print(f"Error: A shoe with code '{code}' already exists")
                return False
            
            product = input("Enter the product name: ").strip()
            if not product:
                logger.warning("Product name cannot be empty")
                print("Error: Product name cannot be empty")
                return False
            
            # Validate cost input
            while True:
                cost = input("Enter the cost (numeric value): ").strip()
                try:
                    cost_value = float(cost)
                    if cost_value < 0:
                        print("Error: Cost cannot be negative. Try again.")
                        continue
                    break
                except ValueError:
                    print("Error: Cost must be a valid number. Try again.")
            
            # Validate quantity input
            while True:
                quantity = input("Enter the quantity (whole number): ").strip()
                try:
                    qty_value = int(quantity)
                    if qty_value < 0:
                        print("Error: Quantity cannot be negative. Try again.")
                        continue
                    break
                except ValueError:
                    print("Error: Quantity must be a valid integer. Try again.")
            
            # Create and add the new shoe
            new_shoe = Shoe(country, code, product, cost, quantity)
            self.shoes_list.append(new_shoe)
            
            
            # Save to file
            if self.save_shoes_data():
                logger.info(f"Added new shoe: {new_shoe}")
                print("Shoe added successfully!")
                return True
            else:
                logger.error("Failed to save shoe data to file")
                print("Error: Failed to save shoe data to file")
                return False
                
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            return False
        except Exception as e:
            logger.error(f"Error adding shoe: {e}")
            print(f"An error occurred: {e}")
            return False
    
    def view_all(self) -> None:
        """
        Display all shoes in the inventory in a formatted table.
        """
        if not self.shoes_list:
            print("\nNo shoes in inventory. Use option 1 to load data or option 2 to add shoes.")
            return
        
        try:
            # Convert shoes to DataFrame for better display
            data = [shoe.to_dict() for shoe in self.shoes_list]
            df = pd.DataFrame(data)
            
            # Format currency columns
            df['Cost'] = df['Cost'].map('${:.2f}'.format)
            df['Value'] = df['Value'].map('${:.2f}'.format)
            
            # Display using tabulate
            print("\n=== Shoe Inventory ===")
            print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
            print(f"\nTotal number of shoes: {len(self.shoes_list)}")
            
        except Exception as e:
            logger.error(f"Error displaying inventory: {e}")
            print(f"Error displaying inventory: {e}")
            # Fallback to simple display if formatting fails
            self._simple_display()
    
    def _simple_display(self) -> None:
        """
        Simple display method as fallback if fancy display fails.
        """
        print("\n=== Shoe Inventory (Simple View) ===")
        for idx, shoe in enumerate(self.shoes_list, 1):
            print(f"{idx}. {shoe}")
        print(f"\nTotal number of shoes: {len(self.shoes_list)}")
    
    def re_stock(self) -> bool:
        """
        Find the shoe with the lowest quantity and restock it.
        
        Returns:
            bool: True if a shoe was restocked successfully, False otherwise
        """
        if not self.shoes_list:
            print("No shoes in inventory to re-stock.")
            return False
        
        try:
            # Find shoes with lowest quantity
            min_quantity = min(shoe.get_quantity() for shoe in self.shoes_list)
            lowest_quantity_shoes = [shoe for shoe in self.shoes_list if shoe.get_quantity() == min_quantity]
            
            # Create a DataFrame for better display
            data = [shoe.to_dict() for shoe in lowest_quantity_shoes]
            df = pd.DataFrame(data)
            df['Cost'] = df['Cost'].map('${:.2f}'.format)
            df['Value'] = df['Value'].map('${:.2f}'.format)
            
            print("\n=== Shoes with Lowest Quantity ===")
            print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=True))
            
            # If multiple shoes have the same lowest quantity, let the user choose
            selected_shoe = None
            if len(lowest_quantity_shoes) > 1:
                while True:
                    try:
                        idx = int(input("\nEnter the index number of the shoe to restock (or -1 to cancel): "))
                        if idx == -1:
                            print("Restock operation cancelled.")
                            return False
                        if 0 <= idx < len(lowest_quantity_shoes):
                            selected_shoe = lowest_quantity_shoes[idx]
                            break
                        else:
                            print(f"Please enter a valid index between 0 and {len(lowest_quantity_shoes)-1}")
                    except ValueError:
                        print("Please enter a valid number")
            else:
                selected_shoe = lowest_quantity_shoes[0]
            
            print(f"\nSelected shoe for restocking: {selected_shoe}")
            choice = input("Do you want to add more quantity to this shoe? (yes/no): ").lower()
            if choice != 'yes':
                return False
            
            # Validate quantity input
            current_qty = selected_shoe.get_quantity()
            while True:
                try:
                    add_quantity = int(input("Enter the quantity to add: "))
                    if add_quantity < 0:
                        print("Quantity cannot be negative. Try again.")
                        continue
                    break
                except ValueError:
                    print("Please enter a valid number.")
            
            # Update quantity and save
            selected_shoe.update_quantity(current_qty + add_quantity)
            
            if self.save_shoes_data():
                logger.info(f"Restocked {selected_shoe.product} (Code: {selected_shoe.code}) with {add_quantity} units")
                print(f"Shoe restocked successfully! New quantity: {selected_shoe.get_quantity()}")
                return True
            else:
                logger.error("Failed to save updated inventory after restocking")
                print("Error: Failed to save updated inventory")
                return False
                
        except Exception as e:
            logger.error(f"Error during restocking: {e}")
            print(f"An error occurred during restocking: {e}")
            return False
    
    def search_shoe(self) -> Optional[List[Shoe]]:
        """
        Search for shoes by code.
        
        Returns:
            Optional[List[Shoe]]: List of matching shoes, or None if none found
        """
        if not self.shoes_list:
            print("No shoes in inventory to search.")
            return None
        
        try:
            code = input("Enter the shoe code to search: ").strip().upper()
            if not code:
                print("Search code cannot be empty")
                return None
                
            found_shoes = [shoe for shoe in self.shoes_list if shoe.code.upper() == code]
            
            if found_shoes:
                # Display results in a table
                data = [shoe.to_dict() for shoe in found_shoes]
                df = pd.DataFrame(data)
                df['Cost'] = df['Cost'].map('${:.2f}'.format)
                df['Value'] = df['Value'].map('${:.2f}'.format)
                
                print("\n=== Search Results ===")
                print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
                return found_shoes
            else:
                print(f"No shoes found with code '{code}'")
                return None
                
        except Exception as e:
            logger.error(f"Error searching for shoes: {e}")
            print(f"An error occurred during search: {e}")
            return None
    
    def value_per_item(self) -> None:
        """
        Calculate and display the value of each item (cost * quantity).
        """
        if not self.shoes_list:
            print("No shoes in inventory.")
            return
        
        try:
            # Create a DataFrame for better display
            data = [shoe.to_dict() for shoe in self.shoes_list]
            df = pd.DataFrame(data)
            
            # Calculate total inventory value
            total_value = df["Value"].sum()
            
            # Format currency columns
            df['Cost'] = df['Cost'].map('${:.2f}'.format)
            df['Value'] = df['Value'].map('${:.2f}'.format)
            
            # Sort by value (highest to lowest)
            df = df.sort_values(by='Value', ascending=False)
            
            print("\n=== Inventory Value Analysis ===")
            print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
            print(f"\nTotal inventory value: ${total_value:.2f}")
            
            # Add basic data visualization if there are enough shoes
            if len(self.shoes_list) >= 3:
                try:
                    self._display_value_chart(df)
                except Exception as e:
                    logger.warning(f"Could not display value chart: {e}")
                    
        except Exception as e:
            logger.error(f"Error calculating inventory values: {e}")
            print(f"An error occurred: {e}")
    
    def _display_value_chart(self, df: pd.DataFrame) -> None:
        """
        Display a basic chart of inventory values using ASCII art.
        
        Args:
            df (pd.DataFrame): DataFrame containing shoe data
        """
        # Convert Value column back to numeric for charting
        numeric_df = pd.DataFrame()
        numeric_df['Product'] = df['Product']
        numeric_df['Value'] = pd.to_numeric(df['Value'].str.replace('$', '').str.replace(',', ''))
        
        # Get top 5 items by value
        top_items = numeric_df.nlargest(5, 'Value')
        
        # Create a simple ASCII bar chart
        max_value = top_items['Value'].max()
        bar_width = 50  # Maximum width of bar
        
        print("\n=== Top 5 Items by Value ===")
        for _, row in top_items.iterrows():
            product = row['Product']
            value = row['Value']
            rel_width = int((value / max_value) * bar_width)
            bar = '█' * rel_width
            print(f"{product[:15]:15} | {bar} ${value:.2f}")
    
    def highest_qty(self) -> Optional[Shoe]:
        """
        Find and display the shoe with the highest quantity.
        
        Returns:
            Optional[Shoe]: The shoe with highest quantity, or None if inventory is empty
        """
        if not self.shoes_list:
            print("No shoes in inventory.")
            return None
        
        try:
            highest_quantity_shoe = max(self.shoes_list, key=lambda x: x.get_quantity())
            
            # Create a DataFrame for display
            data = [highest_quantity_shoe.to_dict()]
            df = pd.DataFrame(data)
            df['Cost'] = df['Cost'].map('${:.2f}'.format)
            df['Value'] = df['Value'].map('${:.2f}'.format)
            
            print("\n=== Shoe with Highest Quantity ===")
            print(tabulate(df, headers="keys", tablefmt="fancy_grid", showindex=False))
            print(f"{highest_quantity_shoe.product} (Code: {highest_quantity_shoe.code}) is for sale!")
            
            return highest_quantity_shoe
            
        except Exception as e:
            logger.error(f"Error finding highest quantity shoe: {e}")
            print(f"An error occurred: {e}")
            return None


def get_valid_choice(min_val: int, max_val: int) -> int:
    """
    Get a valid menu choice from the user.
    
    Args:
        min_val (int): Minimum valid value
        max_val (int): Maximum valid value
        
    Returns:
        int: User's validated choice
    """
    while True:
        try:
            choice = input(f"Enter your choice ({min_val}-{max_val}): ")
            choice_num = int(choice)
            if min_val <= choice_num <= max_val:
                return choice_num
            else:
                print(f"Please enter a number between {min_val} and {max_val}.")
        except ValueError:
            print("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print("\nProgram terminated by user.")
            sys.exit(0)


def display_menu() -> None:
    """Display the main menu options"""
    print("\n" + "="*50)
    print("SHOE INVENTORY MANAGEMENT SYSTEM")
    print("="*50)
    print("1. Read Shoes Data from File")
    print("2. Add New Shoe")
    print("3. View All Shoes")
    print("4. Re-stock Shoes")
    print("5. Search for a Shoe")
    print("6. Calculate Value Per Item")
    print("7. Find Highest Quantity Shoe")
    print("8. Exit")
    print("="*50)


def main() -> None:
    """
    Main function to run the program.
    Handles the program flow and user interaction.
    """
    try:
        print("\nWelcome to the Enhanced Shoe Inventory Management System!")
        
        # Create inventory manager
        inventory = InventoryManager()
        
        # Try to load data at startup
        try:
            if os.path.exists(INVENTORY_FILE):
                inventory.read_shoes_data()
        except Exception as e:
            logger.error(f"Error loading initial data: {e}")
        
        while True:
            # Display menu and get user choice
            display_menu()
            choice = get_valid_choice(1, 8)
            
            if choice == 1:  # Read Shoes Data
                inventory.read_shoes_data()
            elif choice == 2:  # Capture Shoes
                inventory.capture_shoes()
            elif choice == 3:  # View All
                inventory.view_all()
            elif choice == 4:  # Re-stock
                inventory.re_stock()
            elif choice == 5:  # Search Shoe
                inventory.search_shoe()
            elif choice == 6:  # Value Per Item
                inventory.value_per_item()
            elif choice == 7:  # Highest Quantity
                inventory.highest_qty()
            elif choice == 8:  # Exit
                print("\nThank you for using the Shoe Inventory Management System. Goodbye!")
                break
                
            # Pause before showing menu again
            input("\nPress Enter to continue...")
            
    except KeyboardInterrupt:
        print("\nProgram terminated by user.")
    except Exception as e:
        logger.critical(f"Unhandled exception: {e}")
        print(f"\nAn unexpected error occurred: {e}")
        print("Please check the log file for details.")
    finally:
        print("\nExiting program.")


if __name__ == "__main__":
    main()


