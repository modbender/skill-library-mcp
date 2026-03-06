#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
finance-agent: A custom skill to record company expenses and generate tables.
Data is persisted to a CSV file, with optional Google Drive sync.
"""

import os
import pandas as pd
from datetime import datetime


class FinanceAgent:
    """A class to manage company expenses with CSV persistence."""

    def __init__(self, csv_path="expense_report.csv"):
        """Initializes the FinanceAgent, loading existing expenses from CSV.

        Args:
            csv_path (str): Path to the CSV file for data persistence.
        """
        self.csv_path = csv_path
        try:
            self.expenses = pd.read_csv(self.csv_path).to_dict("records")
        except FileNotFoundError:
            self.expenses = []

    def _save_expenses(self):
        """Saves the current expense list to the CSV file."""
        if self.expenses:
            df = pd.DataFrame(self.expenses)
            df.to_csv(self.csv_path, index=False)

    def add_expense(self, date: str, category: str, amount: float, description: str):
        """Adds a new expense to the record and saves to CSV.

        Args:
            date (str): The date of the expense in YYYY-MM-DD format.
            category (str): The category of the expense (e.g., 'Office Supplies', 'Travel').
            amount (float): The amount of the expense.
            description (str): A brief description of the expense.
        """
        try:
            # Validate date format
            datetime.strptime(date, "%Y-%m-%d")
            self.expenses.append(
                {
                    "Date": date,
                    "Category": category,
                    "Amount": amount,
                    "Description": description,
                }
            )
            self._save_expenses()
            print(f"Successfully added expense: {description}")
        except ValueError:
            print("Error: Invalid date format. Please use YYYY-MM-DD.")

    def generate_expense_table(self, output_format: str = "dataframe"):
        """Generates a table of all recorded expenses.

        Args:
            output_format (str): The desired output format ('dataframe', 'csv', 'markdown').

        Returns:
            The expense table in the specified format, or None if no expenses.
        """
        if not self.expenses:
            print("No expenses recorded yet.")
            return None

        df = pd.DataFrame(self.expenses)

        if output_format == "csv":
            return df.to_csv(index=False)
        elif output_format == "markdown":
            return df.to_markdown(index=False)
        else:  # Default to dataframe
            return df

    def export_report(self, output_path: str = None, output_format: str = "csv"):
        """Exports the expense report to a file.

        Args:
            output_path (str, optional): The path to save the report. Defaults to the CSV path.
            output_format (str): The format of the report ('csv' or 'markdown').
        """
        if output_path is None:
            output_path = self.csv_path

        data = self.generate_expense_table(output_format=output_format)
        if data:
            with open(output_path, "w") as f:
                f.write(data)
            print(f"Expense report exported to {output_path}")


if __name__ == "__main__":
    # Example Usage
    agent = FinanceAgent()

    # Add some expenses
    agent.add_expense("2026-02-27", "Office Supplies", 55.00, "Printer paper and ink")
    agent.add_expense("2026-02-26", "Travel", 250.75, "Flight to client meeting")
    agent.add_expense("2026-02-25", "Meals", 45.50, "Lunch with a potential partner")

    # Generate and print the expense table in markdown format
    markdown_table = agent.generate_expense_table(output_format="markdown")
    if markdown_table:
        print("\n--- Expense Report ---")
        print(markdown_table)

    # Export the expense report as a CSV file
    agent.export_report(output_path="expense_report.csv", output_format="csv")
