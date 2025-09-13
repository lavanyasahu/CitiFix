#!/usr/bin/env python3
"""
Script to create the first admin user for the Civic Issue Reporting System.
This should only be run once to bootstrap the first admin user.
"""

from auth import Authentication
import sys

def create_first_admin():
    """Create the first admin user"""
    print("Creating first admin user for Civic Issue Reporting System")
    print("=" * 50)
    
    auth = Authentication()
    
    # Get admin details
    username = input("Enter admin username: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")
    phone = input("Enter admin phone: ")
    
    # Validate inputs
    if not all([username, email, password, phone]):
        print("Error: All fields are required")
        return False
    
    if len(password) < 6:
        print("Error: Password must be at least 6 characters")
        return False
    
    # Create admin user
    success = auth.create_admin_user(username, email, password, phone)
    
    if success:
        print(f"\nAdmin user '{username}' created successfully!")
        print("You can now login to the system with admin privileges.")
        return True
    else:
        print("Error: Failed to create admin user. Username or email may already exist.")
        return False

if __name__ == "__main__":
    create_first_admin()