import pandas as pd
from tkinter import Tk, filedialog

def convert_milesplit_to_xcscoreboard(input_file, output_file):
    # Read the input Milesplit CSV file
    df = pd.read_csv(input_file)

    # Create the Racer Name column by concatenating LName and FName
    df['Racer Name'] = df['LName'] + ', ' + df['FName']

    # Rename Gender column to Group
    df['Group'] = df['Gender']

    # Keep only the necessary columns
    xcscoreboard_df = df[['Racer Name', 'Group', 'Team']]

    # Sort by Gender, Team, LName, and FName
    xcscoreboard_df = xcscoreboard_df.sort_values(by=['Group', 'Team', 'Racer Name'])

    # Add Bib# column with numeric values starting from 1
    xcscoreboard_df['Bib#'] = range(1, len(xcscoreboard_df) + 1)

    # Save the transformed file to the output location without the header row
    xcscoreboard_df.to_csv(output_file, index=False, header=False)

def main():
    # Initialize Tkinter root and hide the main window
    root = Tk()
    root.withdraw()

    # Open a file dialog to select the input file
    input_file = filedialog.askopenfilename(title="Select the Milesplit CSV File", filetypes=[("CSV Files", "*.csv")])
    if not input_file:
        print("No file selected. Exiting.")
        return

    # Open a save dialog to specify the output file
    output_file = filedialog.asksaveasfilename(title="Save the XCScoreboard CSV File", defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
    if not output_file:
        print("No output file specified. Exiting.")
        return

    # Perform the conversion
    convert_milesplit_to_xcscoreboard(input_file, output_file)
    print(f"File successfully converted and saved to {output_file}")

if __name__ == "__main__":
    main()
