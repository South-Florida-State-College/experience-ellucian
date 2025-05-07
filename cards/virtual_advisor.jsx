import React, { useState } from 'react';
import { DataQueryProvider } from '@ellucian/experience-extension-extras';
import { PathCard, PathTypography } from '@ellucian/react-path';
import ChatBot from 'react-chatbot-kit';
import 'react-chatbot-kit/build/main.css';

// Simulated chatbot config (replace with Dialogflow integration)
const botConfig = {
  initialMessages: [
    { id: 1, message: 'Hi! Ask me about your degree progress.', createdBy: 'bot' }
  ]
};

// Simulated action provider (replace with API-driven logic)
const ActionProvider = ({ createChatBotMessage, setState, state }) => {
  const handleGraduationQuery = () => {
    const botMessage = createChatBotMessage('Checking your progress...');
    setState((prev) => ({
      ...prev,
      messages: [...prev.messages, botMessage]
    }));
    // Simulate API response (replace with actual query)
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

// Message parser for user input
const MessageParser = ({ children, actions }) => {
  const parse = (message) => {
    if (message.toLowerCase().includes('graduate') || message.toLowerCase().includes('credits')) {
      actions.handleGraduationQuery();
    } else {
      actions.createChatBotMessage('Sorry, I can only help with graduation progress for now.');
    }
  };

  return <div>{React.cloneElement(children, { parse })}</div>;
};

// GraphQL query for degree progress
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
Yes, you can absolutely create a **Virtual Advisor Card** in **Ellucian Experience** to offer 24/7 guidance, such as notifying students about their graduation requirements (e.g., “You need 3 more credits for graduation”) via an AI chatbot embedded in the dashboard. This is a powerful way to automate student advising, enhance engagement, and provide personalized support. Leveraging **Ellucian Ethos Integration** APIs, the **Ellucian Experience SDK**, and an AI chatbot framework, you can build a card that pulls real-time student data and delivers actionable insights. Below, I’ll outline how to implement this, including a sample code snippet for the card, tailored to your role as an Application Systems Analyst in higher education.

### Why a Virtual Advisor Card?
The Virtual Advisor Card uses AI to analyze student data (e.g., credits earned, program requirements) and provides personalized guidance through a chatbot interface. This automates routine advising tasks, reduces advisor workload, and ensures students receive timely, accurate information. The card integrates with your Student Information System (SIS) like Banner or Colleague via Ethos APIs, ensuring real-time data accuracy.

### Steps to Implement the Virtual Advisor Card

#### 1. **Define the Card’s Functionality**
- **Purpose**: Deliver personalized advising messages (e.g., credits needed, missing prerequisites) and answer common questions (e.g., “What courses should I take next?”).
- **Features**:
  - Display a chatbot interface within the card.
  - Pull student data (e.g., `student-academic-programs`, `student-transcript-credits`) to assess degree progress.
  - Provide AI-driven responses based on predefined rules or a trained model.
  - Ensure FERPA compliance by securing data access.
- **User Experience**: Students see a card on their Ellucian Experience dashboard with a chat window. Typing “Am I on track to graduate?” triggers a response like, “You need 3 more credits in your major.”

#### 2. **Set Up API Configuration with Ethos Integration**
Ethos APIs will provide the student data needed for the chatbot’s responses.
- **Prerequisites**:
  - Ensure Ethos Integration is deployed at your institution.
  - Obtain an **Ethos API Key** or **Bearer Token** for authentication.
- **Identify Data Resources**:
  - `student-academic-programs`: Tracks degree program and requirements.
  - `student-transcript-credits`: Provides earned credits.
  - `course-registrations`: Lists enrolled courses for prerequisite checks.
  - Use the Ethos Data Model (EEDM) documentation to map these resources.
- **Choose API Type**:
  - **GraphQL**: Preferred for fetching nested data (e.g., program requirements and credits in one query). Example query:
    graphql
    query($studentId: ID!) {
      studentAcademicPrograms(filter: { personId: $studentId }) {
        program { title, requiredCredits }
        creditsEarned
      }
    }

  - **REST (EEDM)**: Use for simpler data pulls if GraphQL setup is complex.
- **Configure Data Access**:
  - Use **Ellucian Data Access** to assign resources to your Experience application.
  - Set role-based permissions (e.g., only students access their own data).
  - Use **Data Connect Serverless APIs** for secure, browser-based calls.

#### 3. **Integrate an AI Chatbot Framework**
To provide AI-driven responses, integrate a chatbot framework compatible with Ellucian Experience.
- **Options**:
  - **Dialogflow (Google)**: Easy to set up, supports natural language processing (NLP).
  - **Microsoft Bot Framework**: Integrates well with Azure and Microsoft 365.
  - **Custom Solution**: Build a rule-based chatbot using JavaScript if AI complexity is low.
- **Setup**:
  - For Dialogflow, create an agent and define intents (e.g., “Check graduation status”).
  - Train the agent with phrases like “Am I on track?” and map to API-driven responses.
  - Use webhook fulfillment to call Ethos APIs for real-time data.
- **Example Intent**:
  - **User Input**: “How many credits do I need to graduate?”
  - **Response**: Query `student-academic-programs`, calculate `requiredCredits - creditsEarned`, and return, “You need 3 more credits.”

#### 4. **Develop the Card Using Ellucian Experience SDK**
The card will embed the chatbot UI and fetch student data.
- **Setup**:
  - Clone the `experience-sdk-sample-extensions` GitHub repository.
  - Install Node.js and SDK dependencies.
  - Use the **Ellucian Path Design System** for a consistent, accessible UI.
- **Key Components**:
  - Use `DataQueryProvider` (from `experience-extension-extras`) to handle GraphQL queries.
  - Embed the chatbot using a library like `react-chatbot-kit` or Dialogflow’s web widget.
  - Cache API responses (e.g., credits data) for 24 hours to reduce load.
- **Accessibility**:
  - Ensure the chatbot supports screen readers (WCAG 2.1 compliance).
  - Use `ReactIntlProviderWrapper` for multilingual support.

#### 5. **Test and Deploy**
- **Testing**:
  - Test in a sandbox environment to verify API data retrieval and chatbot responses.
  - Simulate student queries (e.g., “What’s my degree progress?”) to ensure accuracy.
  - Handle errors gracefully (e.g., display “Data unavailable, try again”).
- **Deployment**:
  - Deploy the card via the Experience Configuration page as an admin.
  - Assign to the “Student” persona for dashboard visibility.
- **Monitoring**:
  - Use Ethos logs to track API performance.
  - Collect user feedback to refine chatbot intents.

#### 6. **Ensure Compliance and Security**
- **FERPA**: Restrict data access to the authenticated student’s ID.
- **GDPR** (if applicable): Allow students to opt out of data processing.
- **Security**: Use HTTPS for API calls and secure tokens for authentication.

### Sample Code for the Virtual Advisor Card
Below is a simplified example of a card that integrates a chatbot and fetches degree progress data. This assumes you’re using **React**, the **Experience SDK**, and a basic chatbot UI with `react-chatbot-kit`. For a production environment, you’d integrate Dialogflow or a similar AI framework.


### Notes on the Code
- **Structure**: The card uses the **Path Design System** (`PathCard`) for UI consistency and `DataQueryProvider` for GraphQL queries.
- **Chatbot**: `react-chatbot-kit` is used for simplicity. In production, replace with Dialogflow’s web widget, configured to call Ethos APIs via webhooks.
- **Data**: The `GET_PROGRESS` query fetches degree progress. Replace `personId` with the authenticated student’s ID from Ethos Identity.
- **Customization**: Add intents for more queries (e.g., “What courses next?”) and style the chatbot to match your institution’s branding.
- **Caching**: Implement caching with `useQuery` options to reduce API calls.
- **Dependencies**: Ensure `react-chatbot-kit` and `@ellucian` packages are installed via npm.

### Deployment and Testing
- **Sandbox**: Test in a non-production environment to verify API connectivity and chatbot accuracy.
- **Pilot**: Deploy to a small student group and collect feedback on usability.
- **Monitoring**: Use Ethos logs to track API performance and Dialogflow analytics for chat interactions.

### Impact
- **Students**: Get instant, 24/7 guidance, reducing advising wait times.
- **Advisors**: Focus on complex cases, as routine queries are automated.
- **Institution**: Improves retention by ensuring students stay on track.

### Next Steps
- **Enhance AI**: Train the chatbot with more intents (e.g., financial aid queries) using Dialogflow.
- **Integrate**: Add links to related cards (e.g., course registration).
- **Scale**: Expand to faculty or staff with role-specific advising cards.

If you want to refine this card (e.g., add specific intents, integrate Dialogflow, or style it further), or need help with another card idea, let me know! I can also provide a sample webhook for Dialogflow or focus on Banner-specific integration.
```