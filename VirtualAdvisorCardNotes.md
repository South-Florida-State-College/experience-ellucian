# How-To Notes: Building a Virtual Advisor Card in Ellucian Experience

## Overview
The **Virtual Advisor Card** is a custom card for **Ellucian Experience** that provides 24/7 academic guidance to students via an AI chatbot embedded in the dashboard. It uses **Ellucian Ethos Integration** APIs to fetch real-time student data (e.g., credits earned, degree requirements) and delivers personalized responses (e.g., "You need 3 more credits to graduate"). These notes guide you through setup, development, testing, and deployment, ensuring compliance with higher education standards like FERPA.

## Prerequisites
- **Ellucian Systems**: Access to Ellucian Experience and Ethos Integration (connected to an SIS like Banner, Colleague, or PowerCampus).
- **Development Tools**:
  - Node.js (v16+)
  - Visual Studio Code
  - Git (for cloning repositories)
- **Permissions**:
  - Ethos API Key or Bearer Token for authentication.
  - Admin access to Experience Configuration page.
- **Dependencies**:
  - Ellucian Experience SDK
  - `react-chatbot-kit` (or Dialogflow for production)
  - `@ellucian/react-path` and `@ellucian/experience-extension-extras`
- **Knowledge**:
  - Basic React and JavaScript
  - Familiarity with GraphQL and REST APIs
  - Understanding of FERPA and accessibility (WCAG 2.1)

## Step-by-Step Instructions

### 1. Set Up the Development Environment
1. **Install Node.js**:
   - Download and install Node.js from [nodejs.org](https://nodejs.org) (v16 or higher).
   - Verify: `node -v` and `npm -v` in terminal.
2. **Clone the Experience SDK Repository**:
   - Run: `git clone https://github.com/ellucian-developer/experience-sdk-sample-extensions.git`
   - Navigate to the project: `cd experience-sdk-sample-extensions`
3. **Install Dependencies**:
   - Run: `npm install`
   - Add chatbot library: `npm install react-chatbot-kit`
4. **Set Up VS Code**:
   - Open the project folder in VS Code.
   - Install recommended extensions: ESLint, Prettier, GraphQL.
5. **Verify Ethos Access**:
   - Contact your IT team to confirm Ethos Integration is deployed.
   - Obtain an **Ethos API Key** from the Ethos Integration portal.

### 2. Configure Ethos APIs
1. **Identify Data Needs**:
   - Required resources:
     - `student-academic-programs`: Degree program and required credits.
     - `student-transcript-credits`: Earned credits.
   - Reference: Ethos Data Model (EEDM) documentation in the Ellucian Customer Center.
2. **Choose API Type**:
   - **GraphQL**: Use for nested data (e.g., program and credits in one query).
     ```graphql
     query($studentId: ID!) {
       studentAcademicPrograms(filter: { personId: $studentId }) {
         program { title, requiredCredits }
         creditsEarned
       }
     }
     ```
   - **REST**: Optional for simpler queries (e.g., `/student-academic-programs`).
3. **Configure Data Access**:
   - Log in to the Ethos Integration portal.
   - Assign resources (`student-academic-programs`, `student-transcript-credits`) to your Experience app via **Ellucian Data Access**.
   - Set permissions: Restrict to authenticated student’s `personId`.
4. **Test API**:
   - Use Postman or VS Code’s REST Client extension to test GraphQL queries.
   - Example: Query `studentAcademicPrograms` with a test student ID.

### 3. Integrate an AI Chatbot
1. **Choose a Framework**:
   - **Development**: Use `react-chatbot-kit` for simplicity (rule-based).
   - **Production**: Use **Dialogflow** (Google) for NLP and scalability.
2. **Set Up Dialogflow (Production)**:
   - Create a Dialogflow agent at [dialogflow.cloud.google.com](https://dialogflow.cloud.google.com).
   - Define intents:
     - Intent: “Check Graduation Status”
       - Training Phrases: “Am I on track to graduate?”, “How many credits do I need?”
       - Response: Call Ethos API to calculate `requiredCredits - creditsEarned`.
   - Enable webhook fulfillment:
     - Create a Node.js webhook to query Ethos APIs.
     - Host on a server (e.g., Google Cloud Functions).
3. **Embed Chatbot**:
   - For `react-chatbot-kit`, define `botConfig`, `ActionProvider`, and `MessageParser`.
   - For Dialogflow, embed the web widget in the card.

### 4. Develop the Virtual Advisor Card
1. **Create the Card**:
   - In the `experience-sdk-sample-extensions` folder, create `src/cards/VirtualAdvisorCard.jsx`.
   - Use the following sample code (simplified for development):
     ```jsx
     import React, { useState } from 'react';
     import { DataQueryProvider } from '@ellucian/experience-extension-extras';
     import { PathCard, PathTypography } from '@ellucian/react-path';
     import ChatBot from 'react-chatbot-kit';
     import 'react-chatbot-kit/build/main.css';

     const botConfig = {
       initialMessages: [
         { id: 1, message: 'Hi! Ask me about your degree progress.', createdBy: 'bot' }
       ]
     };

     const ActionProvider = ({ createChatBotMessage, setState }) => {
       const handleGraduationQuery = () => {
         const botMessage = createChatBotMessage('Checking your progress...');
         setState((prev) => ({
           ...prev,
           messages: [...prev.messages, botMessage]
         }));
         setTimeout(() => {
           const response = createChatBotMessage('You need 3 more credits to graduate.');
           setState((prev) => ({
             ...prev,
             messages: [...prev.messages, response]
           }));
         }, 1000);
       };
       return { handleGraduationQuery };
     };

     const MessageParser = ({ children, actions }) => {
       const parse = (message) => {
         if (message.toLowerCase().includes('graduate') || message.toLowerCase().includes('credits')) {
           actions.handleGraduationQuery();
         } else {
           actions.createChatBotMessage('Sorry, I can only help with graduation progress.');
         }
       };
       return <div>{React.cloneElement(children, { parse })}</div>;
     };

     const GET_PROGRESS = `
       query($studentId: ID!) {
         studentAcademicPrograms(filter: { personId: $studentId }) {
           program { title, requiredCredits }
           creditsEarned
         }
       }
     `;

     const VirtualAdvisorCard = ({ cardControl, personId }) => {
       const [chatOpen, setChatOpen] = useState(false);

       return (
         <PathCard
           header="Virtual Advisor"
           subheader="Get 24/7 academic guidance"
           onClick={() => setChatOpen(!chatOpen)}
         >
           <DataQueryProvider
             query={GET_PROGRESS}
             variables={{ studentId: personId }}
             defaultData={{ studentAcademicPrograms: { creditsEarned: 0, program: { requiredCredits: 0 } } }}
           >
             {({ data, loading, error }) => (
               <div>
                 {loading && <PathTypography>Loading...</PathTypography>}
                 {error && <PathTypography>Error loading data.</PathTypography>}
                 {data && chatOpen && (
                   <ChatBot
                     config={botConfig}
                     actionProvider={ActionProvider}
                     messageParser={MessageParser}
                     headerText="Chat with Your Virtual Advisor"
                     placeholderText="Ask about your degree progress"
                     style={{ height: '300px', width: '100%' }}
                   />
                 )}
               </div>
             )}
           </DataQueryProvider>
         </PathCard>
       );
     };

     export default VirtualAdvisorCard;
     ```
2. **Customize the Card**:
   - Replace the simulated response (`You need 3 more credits`) with actual API data:
     ```javascript
     const creditsNeeded = data.studentAcademicPrograms.program.requiredCredits - data.studentAcademicPrograms.creditsEarned;
     const response = createChatBotMessage(`You need ${creditsNeeded} more credits to graduate.`);
     ```
   - Add more intents (e.g., “What courses next?”) by extending `MessageParser`.
3. **Style the Card**:
   - Use the **Path Design System** for consistent UI.
   - Adjust `style` prop for chatbot height/width to fit the dashboard.
4. **Add Accessibility**:
   - Ensure chatbot supports screen readers (e.g., ARIA labels).
   - Use `ReactIntlProviderWrapper` for multilingual support.

### 5. Test the Card
1. **Local Testing**:
   - Run: `npm start` to preview the card in a local Experience environment.
   - Simulate student IDs to test GraphQL queries.
   - Verify chatbot responses for accuracy (e.g., correct credits needed).
2. **Sandbox Testing**:
   - Deploy to a non-production Experience instance.
   - Test with a few student accounts to ensure role-based data access.
3. **Error Handling**:
   - Display fallback messages (e.g., “Data unavailable, try again”) for API failures.
   - Log errors to Ethos for debugging.

### 6. Deploy the Card
1. **Package the Extension**:
   - Run: `npm run build` to create a production bundle.
   - Upload the bundle to the Experience Configuration page.
2. **Configure the Card**:
   - Assign to the “Student” persona for dashboard visibility.
   - Set `customConfiguration` for role-specific settings (e.g., filter by student ID).
3. **Go Live**:
   - Deploy to production after stakeholder approval.
   - Monitor initial usage via Ethos logs and user feedback.

### 7. Ensure Compliance and Security
1. **FERPA**:
   - Restrict API access to the authenticated student’s `personId`.
   - Avoid storing sensitive data in the chatbot.
2. **GDPR** (if applicable):
   - Allow students to opt out of data processing.
   - Document data flows for audits.
3. **Security**:
   - Use HTTPS for API calls.
   - Secure tokens with Ethos Identity.
4. **Accessibility**:
   - Test with screen readers (e.g., NVDA, VoiceOver).
   - Follow WCAG 2.1 guidelines.

### 8. Monitor and Maintain
1. **Performance**:
   - Cache API responses (e.g., credits data) for 24 hours to reduce load.
   - Monitor Ethos API usage in the Integration portal.
2. **User Feedback**:
   - Collect student feedback via surveys to refine chatbot intents.
   - Add new intents (e.g., financial aid queries) based on demand.
3. **Updates**:
   - Update the card for new Ethos API versions or SIS changes.
   - Maintain documentation in this file.

## Troubleshooting
- **API Errors**:
  - Check Ethos logs for authentication or query issues.
  - Verify resource permissions in Data Access.
- **Chatbot Issues**:
  - Ensure Dialogflow webhook is correctly configured.
  - Test intents with varied phrases.
- **Card Not Displaying**:
  - Confirm correct persona assignment in Configuration page.
  - Check browser console for React errors.

## Resources
- **Ellucian Developer Community**: [developer.ellucian.com](https://developer.ellucian.com)
- **GitHub Repos**:
  - `experience-sdk-sample-extensions`
  - `experience-ethos-examples`
- **Documentation**:
  - Ethos Integration Guide
  - Experience SDK Reference
- **Support**: Ellucian Customer Center, Toolkit Developer Forum

## Next Steps
- **Enhance AI**: Integrate Dialogflow for NLP and more intents (e.g., “What’s my next course?”).
- **Expand Functionality**: Add links to related cards (e.g., course registration).
- **Pilot Test**: Deploy to a small student group for feedback.
- **Document Updates**: Update this file with production changes.

*Last Updated: May 07, 2025*