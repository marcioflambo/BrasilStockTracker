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
  - Integration with stock data manager and database system

### 2. Stock Database Manager (stock_database.py)
- **Purpose**: Complete database system for Brazilian stock information
- **Key Features**:
  - Persistent JSON storage with comprehensive stock data
  - On-demand database updates with progress tracking
  - Multi-threaded data collection from Yahoo Finance API
  - Search functionality by name, ticker, or industry
  - Sector-based filtering and browsing
  - Database statistics and status monitoring
  - Automatic cache management with 24-hour expiry

### 3. Stock Data Manager (stock_data.py)
- **Purpose**: Handles real-time stock data retrieval and caching
- **Key Features**:
  - Data caching with 30-second expiry to reduce API calls
  - Error handling for failed stock data requests
  - Batch processing of multiple stock tickers
  - Integration with Yahoo Finance API via yfinance library

### 4. Utility Functions (utils.py)
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

### Dynamic Stock Database System (Updated: July 2025)
The application uses a completely dynamic database system:
- **Zero hardcoded data**: All stock information sourced from dadosdemercado.com.br
- **Web scraping integration**: Uses trafilatura to extract stock data from web
- **JSON-based storage**: Persistent storage with detailed stock information
- **On-demand updates**: Manual database refresh via configuration panel
- **Authentic data only**: No fallback or synthetic stock lists
- **Clean architecture**: Removed all fixed data dependencies
- **Comprehensive coverage**: Dynamic discovery of all B3 stocks
- **Real-time data**: Integration with Yahoo Finance for live prices

### Key Features
- Real-time stock price monitoring with comprehensive financial metrics
- Automatic refresh capability every 2 seconds
- Dynamic watchlist management:
  - Search by name or ticker from database
  - Browse by sector from scraped data
  - Manual ticker entry with validation
- Brazilian currency formatting with smart scaling (K, M, B, T)
- Clean UI with simplified configuration panel
- Database statistics showing dynamically loaded stocks
- Error handling for unavailable stocks
- Responsive web interface optimized for stock monitoring

### Recent Changes (July 2025)
- **Complete code cleanup**: Removed all hardcoded stock data
- **Dynamic data only**: Stock information exclusively from dadosdemercado.com.br
- **Simplified architecture**: Removed portfolio and watchlist persistence modules
- **Clean codebase**: Eliminated all fixed stock lists and synthetic fallbacks
- **Streamlined functionality**: Focus on core stock monitoring features
- **Database-driven**: All stock selections filtered from JSON database
- **Enhanced configuration panel**: Reorganized into tabs for better usability (July 11, 2025)
- **BESST methodology integration**: Implemented authentic Luiz Barsi Filho BESST investment strategy (July 11, 2025)
- **Improved UI organization**: Combined filters and selection into single tab for better workflow
- **Authentic investment criteria**: Applied real BESST sectors (Bancos, Energia, Saneamento, Seguros, Telecomunicações)
- **Performance optimization**: Reduced sample size for faster filtering without compromising accuracy