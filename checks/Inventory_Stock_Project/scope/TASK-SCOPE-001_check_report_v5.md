# Scope Check Report — v5

**Trainee:** Inventory_Stock_Project
**Product:** Purchase
**Date:** 2026-09-24
**Score:** 81/100 (Good)

## Section Scores

| Section | Weight | Score | Notes |
|---|---|---|---|
| Identity | 14 | 88 | All fields present; scope owner [USER INPUT REQUIRED] placeholder unfilled |
| Description | 14 | 85 | Clear domain summary; product-to-project relationship well-described |
| Objects in Scope | 14 | 82 | Core tables, integration layer, and sequences documented; conformed dims correctly scoped as read dependencies |
| Calculation Surface | 14 | 80 | Procedures and analytics layer included |
| Consumers | 15 | 62 | analytics.v_ordertoyearanalytics missing — key cross-domain consumer via correlated subquery |
| Boundaries | 14 | 78 | Out-of-scope items listed; USER INPUT placeholders unfilled |
| Priority and Sequencing | 15 | 75 | Present but less detailed than reference |

## Auto-deducts

None.

## Summary

The product scope document scored 81/100 (Good), with strong coverage across Identity, Description, Objects in Scope, and Calculation Surface sections. The Consumers section is the main weak point — analytics.v_ordertoyearanalytics is missing, which reads fact.purchase via correlated subquery and is a key downstream consumer. The Priority and Sequencing section also lacks detail compared to the reference. The top fix is to add analytics.v_ordertoyearanalytics to Consumers with a coordination note, worth up to +4 pts. Filling the [USER INPUT REQUIRED] placeholders recovers another +2 pts.

## Priority Actions

1. Add analytics.v_ordertoyearanalytics to Consumers section with cross-domain coordination note — +4 pts
2. Fill [USER INPUT REQUIRED] placeholders in Boundaries section — +2 pts
