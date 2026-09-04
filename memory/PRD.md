# ShinDora Nesub - Product Requirement Document (PRD)

## Project Overview
ShinDora Nesub is a full-stack retro anime streaming platform specifically optimized for mobile and desktop screens. It features an admin panel, a moderator panel, and real-time donation integrations with interactive floating overlays.

## Core Features
- **Retro Anime Catalog**: Auto-seeded Doraemon, Crayon Shin-chan, and other retro anime lists.
- **Admin Dashboard**: Comprehensive video CRUD, category management, ads management, user management, and settings configuration.
- **Donation Overlays**: Interactive, real-time donation overlays from Saweria, Trakteer, and Tako.id.
- **Security Key Masking**: Sensitive keys (Stream Keys, API keys, SMTP credentials) are masked on the frontend (`GET /settings`) and securely restored on save (`POST /settings`).
- **Quota Check**: Duplicate vote prevention on polling options with `userId` and `pollId` tracking.
