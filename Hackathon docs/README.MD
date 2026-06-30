This project implements an Agentic AI–powered insurance underwriting system using
Amazon Bedrock AgentCore,  Anthropic Claude-Sonet 4.5 LLM, FastAPI microservices, Angular UI,and PostgreSQL on AWS RDS.

The system automates underwriting decisions by combining:
- Rule-based pre-checks
- LLM-driven agent reasoning
- Persistent audit and decision storage

It is designed to be cloud-native, scalable, and production-ready.
It runs underwriting in two stages/phases:

Phase	   Who runs it	                         Purpose	                             Speed
Phase-1    Pre-check Backend rules	             Fast screening, sanity checks	         Very fast
Phase-2    Final underwriting Crew/LLM+tools	 Deep risk analysis & reasoning	         Slower, richer

This mirrors real insurers (AIG, Prudential, MetLife, etc.).

KEY FEATUES
- Agentic underwriting  Amazon Bedrock AgentCore(Supports dynamic Scaling, App Security, observability)
- Containerized agent runtime hosted on AWS
- FastAPI backend for API exposure
- CREW AI Framework for orchestration of Agentic AI Workflow
- PostgreSQL (AWS RDS) for underwriting data persistence
- Implemented a caching layer to serve frequently accessed data & avoid unnecessary database queries
- End-to-end observability via  AWS CloudWatch
- Swagger/OpenAPI support for testing
- Angular UI for graphical Interface
