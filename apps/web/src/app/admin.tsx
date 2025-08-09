import React from 'react';
import Shell from '../components/layout/Shell';
import PageHeader from '../components/layout/PageHeader';

export default function Admin() {
  return (
    <Shell title="Admin" showBackButton={true}>
      <div className="p-4 sm:p-6 lg:p-8">
        <PageHeader
          title="Admin Dashboard"
          subtitle="Manage system settings and configurations"
          breadcrumbs={[
            { label: 'Dashboard', href: '/dashboard' },
            { label: 'Admin' },
          ]}
        />
        <div className="mt-6 grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="col-span-2 radius-12 elev-sm bg-white p-4">
            <div className="font-medium mb-2">System Overview</div>
            <div className="text-sm text-slate-600">
              This is a placeholder for the admin dashboard. In a real application, this would show system metrics, user management, and other administrative functions.
            </div>
          </div>
          <div className="radius-12 elev-sm bg-white p-4">
            <div className="font-medium mb-2">Quick Actions</div>
            <ul className="text-sm text-slate-600 list-disc pl-5 space-y-1">
              <li>Manage users</li>
              <li>Configure settings</li>
              <li>View logs</li>
              <li>System maintenance</li>
            </ul>
          </div>
        </div>
      </div>
    </Shell>
  );
}