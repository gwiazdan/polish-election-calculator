# ARCHITECTURE: Polish Election Calculator

**Author**: gwiazdan  
**Created**: 06-02-2026  
**Version:** 0.1  


## Components

### Frontend (React + Typescript)

**Responsibilities**
- Render interactive map
- Execute vote distribution calculations
- Display results
- Manage user scenarios

**Key Libraries**
- TODO

**Why client-side calculations?**
- Offloads computation from backend
- Instant feedback


### Backend (FastAPI)

**Responsibilities**
- Spatial data aggregation
- Provide election context
- Serve map geometries
- Expose calculation algorithms as portable functions

**Key Libraries**
- TODO


### Database (PostgresSQL)

### Cache (Redis)