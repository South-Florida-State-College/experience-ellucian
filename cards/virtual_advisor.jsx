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


