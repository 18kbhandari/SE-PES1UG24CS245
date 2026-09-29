# Lab 3 – Written Justification
**Self-Service Coffee Kiosk | PES1UG24CS245**

## Architecture Selection
We chose **Layered Architecture** for the Self-Service Coffee Kiosk System.

### Architectural Choice
The system is organized into Presentation, Business, and Data/Hardware layers. The Presentation layer handles the touch screen, the Business layer contains the Order Manager and Payment Service, and the Data/Hardware layer handles menu/pricing storage and receipt printing.

### Reason 1 – Clear separation of responsibilities
The kiosk has distinct responsibilities: customer interaction, order/payment processing, and menu/pricing plus printer access. Layered architecture keeps these responsibilities separate, making the design easier to understand and maintain.

### Reason 2 – Suitable for a focused kiosk application
The scenario is a single kiosk workflow with a small set of coffee types, sizes, and one payment method. A layered design avoids the operational complexity of multiple independently deployed services while still giving clear component boundaries.

### Security Advantage
Payment processing is isolated inside the Payment Service rather than being mixed with the touch screen or database logic. Access between layers can be restricted so only the required payment operations are exposed, reducing unnecessary access to payment-related functionality.

### Performance Benefit
Most interactions remain within the kiosk through direct component/service communication, avoiding the additional network latency and operational overhead associated with a distributed microservices deployment. Menu and pricing data can also be retrieved directly from the local data component.

### Conclusion
The selected architecture provides clear responsibility boundaries, straightforward deployment, and a simple communication path for this kiosk scenario.
