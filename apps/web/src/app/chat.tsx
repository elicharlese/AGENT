import React from 'react';
import { Shell } from '../components/layout/Shell';
import IMessageChat from '../components/chat/IMessageChat';

export default function Chat() {
  return (
    <Shell>
      <div className="h-[calc(100vh-3.5rem)] p-0">
        <IMessageChat />
      </div>
    </Shell>
  );
}
