## Quick Reference -- Key Facts for Retrieval

- Type: Cinematic web application, built for competition
- Competition: Replit 10 Year Buildathon
- Data source: NASA open data (APOD, planetary, asteroid, Earth imagery APIs)
- Components: Daily Space Exhibition, Planetary Archive, Asteroid Watch,
  Earth Pulse, Presenter Mode, Control Room Mode
- Demonstrates: full-stack web development, creative direction, public API integration,
  shipping under competition deadline

---

# Case Study: FAROUT
*Replit 10 Year Buildathon*

## What It Is

A cinematic browser experience built around the aesthetics of deep space and NASA open data. Built for the Replit 10 Year Buildathon — a competition requiring participants to build and ship a complete project within the competition timeframe.

FAROUT treats NASA's publicly available data not as a database to query but as a design material — something to present in a way that communicates scale, distance, and strangeness without requiring any scientific background from the viewer.

---

## The Components

**Daily Space Exhibition**
Powered by NASA's Astronomy Picture of the Day (APOD) API. Each day's image is presented as a gallery exhibit rather than a data entry — full-screen, typographically considered, with curatorial framing that makes the astronomical context legible to a non-specialist. Changes every day automatically.

**Planetary Archive**
A curated gallery of planetary imagery drawn from NASA sources. The design language is archival rather than encyclopedic — presentation prioritizing visual impact over data density. The intent is to make someone want to look, not to make them want to learn facts.

**Asteroid Watch**
Near-Earth asteroid data presented as a readable digest. The challenge was translating orbital mechanics data (distance, velocity, threat classification) into something a person without an astrophysics background could actually interpret. The design solution was to use scale analogies and visual distance metaphors rather than raw numbers alone.

**Earth Pulse**
Full-disk Earth imagery, sourced from NASA's real-time satellite feeds. Presented as a live view rather than a static image — the experience of seeing the whole planet as a continuous object rather than a photograph.

**Presenter Mode**
A stripped-down, distraction-free mode for using FAROUT in a presentation context — classrooms, talks, installations. Removes all UI chrome, leaves only the imagery and minimal framing text.

**Control Room Mode**
A multi-panel view inspired by mission control aesthetics. Multiple data streams visible simultaneously: current APOD, live Earth view, asteroid proximity data, recent planetary imagery. Designed for the "space nerd who wants everything on one screen" use case.

---

## What the Build Process Looked Like

The constraint was the competition deadline. FAROUT had to be scoped to what could actually be built and shipped cleanly in the available time, not what was theoretically possible.

The decision to use NASA's open data APIs rather than static content was the core architectural choice. It meant the experience would be different every day without any manual content maintenance — the data provides the variation, the design provides the consistency.

The aesthetic direction (cinematic, archival, dark) was set before the first line of code. Without a visual language decided upfront, iterative development on a project like this produces incoherence. The design system — typography, spacing, color palette, motion — was documented as a small internal reference and applied consistently across all components.

---

## What This Project Demonstrates

- **Full-stack web development:** concept to deployed live application, solo
- **Public API integration:** NASA APOD, Near Earth Object, Earth imagery, planetary APIs
- **Creative direction for interactive experiences:** cinematic aesthetic applied to data presentation
- **Shipping under competitive deadline:** working product delivered within a competition constraint, not a portfolio exercise
- **UX thinking for non-technical audiences:** making complex scientific data legible and engaging without dumbing it down

**Relevant for:** Creative Technologist, front-end and creative development roles, any role where "can you make data beautiful" or "can you ship under pressure" is the question.
