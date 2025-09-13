# Civic Issue Reporting System

## Overview

A web-based civic issue reporting system built with Streamlit that allows citizens to report municipal problems (potholes, garbage, street lights, etc.) with photos and GPS locations. The system includes user authentication, interactive maps for issue visualization, and admin capabilities for managing and resolving reported issues. Citizens can track the status of their reports while administrators can efficiently categorize and address community concerns.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend Architecture
- **Streamlit Web Framework**: Single-page application with sidebar navigation for different user roles (citizens vs admins)
- **Interactive Mapping**: Folium integration for displaying issue locations on interactive maps with category-based color coding
- **Image Handling**: PIL-based image processing with base64 encoding for photo uploads
- **Session Management**: Streamlit session state for user authentication and role-based access control

### Backend Architecture
- **Database Layer**: SQLite database with thread-safe connections and row factory for dictionary-like access
- **Authentication System**: bcrypt-based password hashing with role-based user management (citizen/admin roles)
- **Data Models**: Two main entities - users and issues, with foreign key relationships
- **Utility Functions**: Helper functions for data validation, sanitization, and formatting

### Data Storage
- **SQLite Database**: Local file-based storage with users and issues tables
- **Image Storage**: Base64-encoded images stored directly in database as TEXT fields
- **Location Data**: Latitude/longitude coordinates stored as REAL types for precise mapping

### Security & Validation
- **Password Security**: bcrypt hashing with salt for secure password storage
- **Input Sanitization**: HTML entity encoding to prevent XSS attacks
- **Data Validation**: Email and phone number format validation using regex patterns
- **Session Security**: Environment-based session secrets for authentication

## External Dependencies

### Core Framework Dependencies
- **Streamlit**: Web application framework and UI components
- **streamlit-folium**: Integration layer for Folium maps in Streamlit

### Data & Database
- **pandas**: Data manipulation and DataFrame operations
- **sqlite3**: Built-in Python database interface (no external database required)

### Authentication & Security
- **bcrypt**: Password hashing and verification library

### Mapping & Visualization
- **folium**: Interactive map generation and marker management

### Image Processing
- **PIL (Pillow)**: Image handling, processing, and format conversion

### Utilities
- **uuid**: Unique identifier generation for database records
- **datetime**: Timestamp handling and formatting
- **threading**: Database connection thread safety
- **base64**: Image encoding for database storage
- **re**: Regular expressions for input validation
- **os**: Environment variable access for configuration