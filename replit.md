# Monitor de Ações Brasileiras

## Overview

This is a Brazilian stock market monitoring application built with Streamlit. The application provides real-time tracking of Brazilian stocks (B3 stocks) with features like automatic refresh, watchlist management, and formatted display of financial data. It uses Yahoo Finance as the data source and presents information in a user-friendly dashboard format.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a simple, modular architecture with clear separation of concerns:

- **Frontend**: Streamlit-based web interface providing real-time stock monitoring
- **Data Layer**: Yahoo Finance API integration through yfinance library
- **Business Logic**: Stock data management with caching mechanisms
- **Utilities**: Formatting functions for currency, percentages, and market cap display

## Key Components

### 1. Main Application (app.py)
- **Purpose**: Primary Streamlit application entry point
- **Responsibilities**: 
  - Page configuration and layout management
  - Session state management for watched stocks and auto-refresh settings
  - User interface rendering including sidebar controls
  - Integration with stock data manager

### 2. Stock Data Manager (stock_data.py)
- **Purpose**: Handles all stock data retrieval and caching
- **Key Features**:
  - Data caching with 30-second expiry to reduce API calls
  - Error handling for failed stock data requests
  - Batch processing of multiple stock tickers
  - Integration with Yahoo Finance API via yfinance library

### 3. Utility Functions (utils.py)
- **Purpose**: Provides formatting functions for financial data display
- **Functions**:
  - Currency formatting with Brazilian Real (R$) notation
  - Percentage formatting for stock changes
  - Market cap formatting with appropriate scaling (K, M, B)
  - Locale-aware formatting with fallback mechanisms

## Data Flow

1. **User Input**: Users can add stock tickers through the sidebar interface
2. **Data Retrieval**: StockDataManager fetches data from Yahoo Finance API
3. **Caching**: Retrieved data is cached for 30 seconds to improve performance
4. **Processing**: Raw financial data is processed and formatted using utility functions
5. **Display**: Formatted data is presented in the Streamlit interface
6. **Auto-Refresh**: Optional automatic updates every 2 seconds for real-time monitoring

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework for the user interface
- **yfinance**: Yahoo Finance API client for stock data retrieval
- **pandas**: Data manipulation and analysis
- **locale**: System locale support for Brazilian Portuguese formatting

### Data Source
- **Yahoo Finance**: Primary data source for Brazilian stock market data (B3 exchange)
- **Stock Format**: Uses .SA suffix for Brazilian stocks (e.g., ITUB4.SA, PETR4.SA)

## Deployment Strategy

The application is designed for Replit deployment with the following characteristics:

- **Runtime**: Python-based Streamlit application
- **Dependencies**: Managed through standard Python package management
- **Configuration**: Streamlit page configuration optimized for wide layout
- **Session Management**: Uses Streamlit's built-in session state for data persistence
- **Performance**: Implements caching to minimize API calls and improve response times

### Default Watchlist
The application comes pre-configured with major Brazilian stocks:
- ITUB4.SA (Itaú Unibanco)
- PETR4.SA (Petrobras)
- VALE3.SA (Vale)
- BBDC4.SA (Bradesco)
- ABEV3.SA (Ambev)

### Key Features
- Real-time stock price monitoring
- Automatic refresh capability
- Dynamic watchlist management
- Brazilian currency formatting
- Error handling for unavailable stocks
- Responsive web interface