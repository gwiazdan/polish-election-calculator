# CONCEPT: Polish Election Calculator

**Author**: gwiazdan  
**Created**: 06-02-2026  
**Version:** 0.1  


## Summary
A web application for calculating Polish election outcomes (parliamentary, senate, regional assemblies, and European Parliament) under different vote distribution scenarios. The key idea is to visualize results at local/district levels under different scenarios.

## Technical Approach

The application is split into two segments: backend and frontend. The backend handles all business logic except calculations, which are performed client-side. The frontend should be highly flexible by importing context, parties, maps, and algorithms from the backend instead of defining everything internally.

## Key Features

Precinct-level data storage: Store election results directly at voting precinct `obwód wyborczy` level
Geometry-based aggregation: Aggregate results using spatial operations, not foreign key relationships
Dependency injection: Pluggable models for mapping local support to national support
Modularity and lightweight design: Keep components decoupled and minimal

## Additional Project Paths

- Potential admin panel for data management
- Possible Selenium scraper for PKW (State Electoral Commission) data extraction