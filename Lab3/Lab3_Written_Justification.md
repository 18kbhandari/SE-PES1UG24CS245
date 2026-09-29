# Lab 3 – Written Justification
**Self-Service Coffee Kiosk | PES1UG24CS245**

## Architecture Selection
We chose **Layered Architecture** for the Self-Service Coffee Kiosk System.

### Architectural Choice
The system is divided into Presentation, Business, and Data/Hardware layers. The Presentation layer handles touch-screen interaction; the Business layer handles ordering and payment; and the Data/Hardware layer handles menu/pricing storage and receipt printing.

### Reason 1 – Clear separation of responsibilities
The kiosk has distinct responsibilities: customer interaction, order/payment processing, and menu/pricing plus printer access. Keeping these responsibilities in separate layers makes the component boundaries clear and simplifies maintenance.

### Reason 2 – Suitable for a focused kiosk workflow
The scenario has a small, fixed workflow: three coffee types, two sizes, and credit-card payment only. A layered design keeps this workflow straightforward without introducing the operational complexity of independently deployed services.

### Security Advantage
Payment processing is isolated in the Payment Service instead of being mixed with the touch-screen or database components. Layer boundaries can restrict access so components expose only the operations required by other components.

### Performance Benefit
The kiosk can communicate directly between local components, avoiding unnecessary network hops and distributed-service overhead. Menu and pricing information can also be accessed locally by the kiosk.

### Conclusion
Layered Architecture provides clear separation, simple deployment, and a straightforward communication path for the kiosk scenario.
