'use client';

import { useEffect, useState, useCallback } from 'react';
import TopBar from '../../components/layout/TopBar';
import Sidebar from '../../components/layout/SideBar';
import { getAuditLogs } from '../../lib/api/auditLog';

// ─── Helpers ────────────────────────────────────────────────────────────────

const MODEL_TYPE_COLORS = {
  case:     'bg-blue-100 text-blue-800',
  document: 'bg-purple-100 text-purple-800',
  user:     'bg-green-100 text-green-800',
  firm:     'bg-orange-100 text-orange-800',
  note:     'bg-yellow-100 text-yellow-800',
};

const MODEL_TYPE_LABELS = {
  case: 'Case',
  document: 'Document',
  user: 'User',
  firm: 'Firm',
  note: 'Note',
};

function formatTimestamp(ts) {
  if (!ts) return '—';
  const d = new Date(ts);
  return d.toLocaleString('en-GB', {
    day: '2-digit', month: 'short', year: 'numeric',
    hour: '2-digit', minute: '2-digit',
  });
}

function formatAction(action) {
  if (!action) return '—';
  return action
    .split('_')
    .map(w => w.charAt(0).toUpperCase() + w.slice(1))
    .join(' ');
}

// ─── Changes Detail Drawer ───────────────────────────────────────────────────

function ChangesDrawer({ log, onClose }) {
  if (!log) return null;

  const changes = log.changes || {};
  const hasChanges = Object.keys(changes).length > 0;

  return (
    <div className="fixed inset-0 z-50 flex justify-end">
      <div
        className="absolute inset-0 bg-black/30 backdrop-blur-sm"
        onClick={onClose}
      />
      <div className="relative w-full max-w-md bg-white shadow-2xl flex flex-col h-full z-10">
        <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
          <div>
            <h2 className="text-base font-semibold text-gray-900">
              {formatAction(log.action)}
            </h2>
            <p className="text-xs text-gray-500 mt-0.5">{formatTimestamp(log.timestamp)}</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-5">
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Performed by</span>
              <span className="text-sm text-gray-900">{log.user_email || 'System'}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Record type</span>
              <span
                className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                  MODEL_TYPE_COLORS[log.model_type] || 'bg-gray-100 text-gray-700'
                }`}
              >
                {MODEL_TYPE_LABELS[log.model_type] || log.model_type}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Record ID</span>
              <span className="text-sm text-gray-900">#{log.model_id}</span>
            </div>
            {log.ip_address && (
              <div className="flex items-center justify-between">
                <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">IP Address</span>
                <span className="text-sm font-mono text-gray-700">{log.ip_address}</span>
              </div>
            )}
          </div>

          <div>
            <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
              Changes
            </h3>
            {hasChanges ? (
              <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-800 whitespace-pre-wrap overflow-x-auto font-mono leading-relaxed">
                {JSON.stringify(changes, null, 2)}
              </pre>
            ) : (
              <p className="text-sm text-gray-400 italic">No change data recorded.</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Main Page ───────────────────────────────────────────────────────────────

export default function AuditLogPage() {
  const [collapsed, setCollapsed] = useState(false);

  const [logs, setLogs]           = useState([]);
  const [loading, setLoading]     = useState(true);
  const [error, setError]         = useState('');
  const [page, setPage]           = useState(1);
  const [totalCount, setTotal]    = useState(0);
  const [modelTypeFilter, setModelTypeFilter] = useState('');
  const [selectedLog, setSelectedLog] = useState(null);

  const PAGE_SIZE = 50;
  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  const fetchLogs = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const data = await getAuditLogs({
        page,
        page_size: PAGE_SIZE,
        model_type: modelTypeFilter,
      });
      setLogs(data?.results || []);
      setTotal(data?.count || 0);
    } catch (e) {
      setError(e.message || 'Failed to load audit logs.');
    } finally {
      setLoading(false);
    }
  }, [page, modelTypeFilter]);

  useEffect(() => {
    fetchLogs();
  }, [fetchLogs]);

  const handleFilterChange = (val) => {
    setModelTypeFilter(val);
    setPage(1);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar collapsed={collapsed} setCollapsed={setCollapsed} />

      <div
        className={`transition-all duration-300 ${collapsed ? "ml-[68px]" : "ml-[240px]"}`}
      >
        <TopBar title="Audit Log" />

        <div className="p-6 max-w-7xl mx-auto">
          {/* Header row */}
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
            <div>
              <h1 className="text-xl font-semibold text-gray-900">Activity Log</h1>
              <p className="text-sm text-gray-500 mt-0.5">
                All actions recorded for your firm
                {totalCount > 0 && (
                  <span className="ml-1 font-medium text-gray-700">— {totalCount.toLocaleString()} entries</span>
                )}
              </p>
            </div>

            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600 whitespace-nowrap">Filter by type</label>
              <select
                value={modelTypeFilter}
                onChange={(e) => handleFilterChange(e.target.value)}
                className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-700"
              >
                <option value="">All types</option>
                <option value="case">Case</option>
                <option value="document">Document</option>
                <option value="user">User</option>
                <option value="firm">Firm</option>
                <option value="note">Note</option>
              </select>
            </div>
          </div>

          {/* Table card */}
          <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
            {error && (
              <div className="px-6 py-4 bg-red-50 border-b border-red-100 text-sm text-red-700 flex items-center gap-2">
                <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {error}
              </div>
            )}

            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="bg-gray-50 border-b border-gray-100">
                    <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Timestamp</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Action</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Type</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Record</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Performed by</th>
                    <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">IP</th>
                    <th className="px-6 py-3"></th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {loading ? (
                    Array.from({ length: 8 }).map((_, i) => (
                      <tr key={i} className="animate-pulse">
                        <td className="px-6 py-4"><div className="h-3 w-32 bg-gray-100 rounded" /></td>
                        <td className="px-6 py-4"><div className="h-3 w-28 bg-gray-100 rounded" /></td>
                        <td className="px-6 py-4"><div className="h-5 w-16 bg-gray-100 rounded-full" /></td>
                        <td className="px-6 py-4"><div className="h-3 w-8 bg-gray-100 rounded" /></td>
                        <td className="px-6 py-4"><div className="h-3 w-36 bg-gray-100 rounded" /></td>
                        <td className="px-6 py-4"><div className="h-3 w-24 bg-gray-100 rounded" /></td>
                        <td className="px-6 py-4" />
                      </tr>
                    ))
                  ) : logs.length === 0 ? (
                    <tr>
                      <td colSpan={7} className="px-6 py-16 text-center text-gray-400">
                        <div className="flex flex-col items-center gap-2">
                          <svg className="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                          </svg>
                          <span className="text-sm">No audit log entries found</span>
                        </div>
                      </td>
                    </tr>
                  ) : (
                    logs.map((log) => (
                      <tr
                        key={log.id}
                        className="hover:bg-gray-50/80 transition-colors cursor-pointer"
                        onClick={() => setSelectedLog(log)}
                      >
                        <td className="px-6 py-3.5 text-gray-600 whitespace-nowrap font-mono text-xs">
                          {formatTimestamp(log.timestamp)}
                        </td>
                        <td className="px-6 py-3.5 font-medium text-gray-800">
                          {formatAction(log.action)}
                        </td>
                        <td className="px-6 py-3.5">
                          <span
                            className={`inline-flex items-center text-xs px-2 py-0.5 rounded-full font-medium ${
                              MODEL_TYPE_COLORS[log.model_type] || 'bg-gray-100 text-gray-700'
                            }`}
                          >
                            {MODEL_TYPE_LABELS[log.model_type] || log.model_type}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 text-gray-500 font-mono text-xs">
                          #{log.model_id}
                        </td>
                        <td className="px-6 py-3.5 text-gray-600 max-w-[200px] truncate">
                          {log.user_email || <span className="text-gray-400 italic">System</span>}
                        </td>
                        <td className="px-6 py-3.5 text-gray-400 font-mono text-xs">
                          {log.ip_address || '—'}
                        </td>
                        <td className="px-6 py-3.5 text-right">
                          <button
                            onClick={(e) => { e.stopPropagation(); setSelectedLog(log); }}
                            className="text-xs text-blue-600 hover:text-blue-800 font-medium"
                          >
                            Details
                          </button>
                        </td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>

            {totalPages > 1 && (
              <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100 bg-gray-50/50">
                <span className="text-sm text-gray-500">
                  Page {page} of {totalPages} &middot; {totalCount.toLocaleString()} total entries
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage((p) => Math.max(1, p - 1))}
                    disabled={page === 1 || loading}
                    className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    Previous
                  </button>
                  <button
                    onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                    disabled={page === totalPages || loading}
                    className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      {selectedLog && (
        <ChangesDrawer
          log={selectedLog}
          onClose={() => setSelectedLog(null)}
        />
      )}
    </div>
  );
}

// 'use client';

// import { useEffect, useState, useCallback } from 'react';
// import TopBar from '@/components/layout/TopBar';
// import { getAuditLogs } from '../../lib/api/auditLog';
// // ─── Helpers ────────────────────────────────────────────────────────────────

// const MODEL_TYPE_COLORS = {
//   case:     'bg-blue-100 text-blue-800',
//   document: 'bg-purple-100 text-purple-800',
//   user:     'bg-green-100 text-green-800',
//   firm:     'bg-orange-100 text-orange-800',
//   note:     'bg-yellow-100 text-yellow-800',
// };

// const MODEL_TYPE_LABELS = {
//   case: 'Case',
//   document: 'Document',
//   user: 'User',
//   firm: 'Firm',
//   note: 'Note',
// };

// function formatTimestamp(ts) {
//   if (!ts) return '—';
//   const d = new Date(ts);
//   return d.toLocaleString('en-GB', {
//     day: '2-digit', month: 'short', year: 'numeric',
//     hour: '2-digit', minute: '2-digit',
//   });
// }

// function formatAction(action) {
//   if (!action) return '—';
//   return action
//     .split('_')
//     .map(w => w.charAt(0).toUpperCase() + w.slice(1))
//     .join(' ');
// }

// // ─── Changes Detail Drawer ───────────────────────────────────────────────────

// function ChangesDrawer({ log, onClose }) {
//   if (!log) return null;

//   const changes = log.changes || {};
//   const hasChanges = Object.keys(changes).length > 0;

//   return (
//     <div className="fixed inset-0 z-50 flex justify-end">
//       {/* Backdrop */}
//       <div
//         className="absolute inset-0 bg-black/30 backdrop-blur-sm"
//         onClick={onClose}
//       />

//       {/* Drawer panel */}
//       <div className="relative w-full max-w-md bg-white shadow-2xl flex flex-col h-full z-10">
//         {/* Header */}
//         <div className="flex items-center justify-between px-6 py-4 border-b border-gray-100">
//           <div>
//             <h2 className="text-base font-semibold text-gray-900">
//               {formatAction(log.action)}
//             </h2>
//             <p className="text-xs text-gray-500 mt-0.5">{formatTimestamp(log.timestamp)}</p>
//           </div>
//           <button
//             onClick={onClose}
//             className="p-2 rounded-lg hover:bg-gray-100 transition-colors text-gray-500"
//           >
//             <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
//             </svg>
//           </button>
//         </div>

//         {/* Body */}
//         <div className="flex-1 overflow-y-auto px-6 py-4 space-y-5">
//           {/* Meta */}
//           <div className="space-y-2">
//             <div className="flex items-center justify-between">
//               <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Performed by</span>
//               <span className="text-sm text-gray-900">{log.user_email || 'System'}</span>
//             </div>
//             <div className="flex items-center justify-between">
//               <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Record type</span>
//               <span
//                 className={`text-xs px-2 py-0.5 rounded-full font-medium ${
//                   MODEL_TYPE_COLORS[log.model_type] || 'bg-gray-100 text-gray-700'
//                 }`}
//               >
//                 {MODEL_TYPE_LABELS[log.model_type] || log.model_type}
//               </span>
//             </div>
//             <div className="flex items-center justify-between">
//               <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">Record ID</span>
//               <span className="text-sm text-gray-900">#{log.model_id}</span>
//             </div>
//             {log.ip_address && (
//               <div className="flex items-center justify-between">
//                 <span className="text-xs font-medium text-gray-500 uppercase tracking-wide">IP Address</span>
//                 <span className="text-sm font-mono text-gray-700">{log.ip_address}</span>
//               </div>
//             )}
//           </div>

//           {/* Changes */}
//           <div>
//             <h3 className="text-xs font-medium text-gray-500 uppercase tracking-wide mb-3">
//               Changes
//             </h3>
//             {hasChanges ? (
//               <pre className="bg-gray-50 border border-gray-200 rounded-lg p-3 text-xs text-gray-800 whitespace-pre-wrap overflow-x-auto font-mono leading-relaxed">
//                 {JSON.stringify(changes, null, 2)}
//               </pre>
//             ) : (
//               <p className="text-sm text-gray-400 italic">No change data recorded.</p>
//             )}
//           </div>
//         </div>
//       </div>
//     </div>
//   );
// }

// // ─── Main Page ───────────────────────────────────────────────────────────────

// export default function AuditLogPage() {
//   const [logs, setLogs]           = useState([]);
//   const [loading, setLoading]     = useState(true);
//   const [error, setError]         = useState('');
//   const [page, setPage]           = useState(1);
//   const [totalCount, setTotal]    = useState(0);
//   const [modelTypeFilter, setModelTypeFilter] = useState('');
//   const [selectedLog, setSelectedLog] = useState(null);

//   const PAGE_SIZE = 50;
//   const totalPages = Math.ceil(totalCount / PAGE_SIZE);

//   const fetchLogs = useCallback(async () => {
//     setLoading(true);
//     setError('');
//     try {
//       const data = await getAuditLogs({
//         page,
//         page_size: PAGE_SIZE,
//         model_type: modelTypeFilter,
//       });
//       setLogs(data?.results || []);
//       setTotal(data?.count || 0);
//     } catch (e) {
//       setError(e.message || 'Failed to load audit logs.');
//     } finally {
//       setLoading(false);
//     }
//   }, [page, modelTypeFilter]);

//   useEffect(() => {
//     fetchLogs();
//   }, [fetchLogs]);

//   // Reset to page 1 when filter changes
//   const handleFilterChange = (val) => {
//     setModelTypeFilter(val);
//     setPage(1);
//   };

//   return (
//     <div className="min-h-screen bg-gray-50">
//       <TopBar title="Audit Log" />

//       <div className="p-6 max-w-7xl mx-auto">
//         {/* Header row */}
//         <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
//           <div>
//             <h1 className="text-xl font-semibold text-gray-900">Activity Log</h1>
//             <p className="text-sm text-gray-500 mt-0.5">
//               All actions recorded for your firm
//               {totalCount > 0 && (
//                 <span className="ml-1 font-medium text-gray-700">— {totalCount.toLocaleString()} entries</span>
//               )}
//             </p>
//           </div>

//           {/* Filter */}
//           <div className="flex items-center gap-2">
//             <label className="text-sm text-gray-600 whitespace-nowrap">Filter by type</label>
//             <select
//               value={modelTypeFilter}
//               onChange={(e) => handleFilterChange(e.target.value)}
//               className="text-sm border border-gray-200 rounded-lg px-3 py-2 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500 text-gray-700"
//             >
//               <option value="">All types</option>
//               <option value="case">Case</option>
//               <option value="document">Document</option>
//               <option value="user">User</option>
//               <option value="firm">Firm</option>
//               <option value="note">Note</option>
//             </select>
//           </div>
//         </div>

//         {/* Table card */}
//         <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
//           {error && (
//             <div className="px-6 py-4 bg-red-50 border-b border-red-100 text-sm text-red-700 flex items-center gap-2">
//               <svg className="w-4 h-4 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                 <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
//               </svg>
//               {error}
//             </div>
//           )}

//           <div className="overflow-x-auto">
//             <table className="w-full text-sm">
//               <thead>
//                 <tr className="bg-gray-50 border-b border-gray-100">
//                   <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Timestamp</th>
//                   <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Action</th>
//                   <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Type</th>
//                   <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Record</th>
//                   <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">Performed by</th>
//                   <th className="text-left px-6 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wide">IP</th>
//                   <th className="px-6 py-3"></th>
//                 </tr>
//               </thead>
//               <tbody className="divide-y divide-gray-50">
//                 {loading ? (
//                   // Skeleton rows
//                   Array.from({ length: 8 }).map((_, i) => (
//                     <tr key={i} className="animate-pulse">
//                       <td className="px-6 py-4"><div className="h-3 w-32 bg-gray-100 rounded" /></td>
//                       <td className="px-6 py-4"><div className="h-3 w-28 bg-gray-100 rounded" /></td>
//                       <td className="px-6 py-4"><div className="h-5 w-16 bg-gray-100 rounded-full" /></td>
//                       <td className="px-6 py-4"><div className="h-3 w-8 bg-gray-100 rounded" /></td>
//                       <td className="px-6 py-4"><div className="h-3 w-36 bg-gray-100 rounded" /></td>
//                       <td className="px-6 py-4"><div className="h-3 w-24 bg-gray-100 rounded" /></td>
//                       <td className="px-6 py-4" />
//                     </tr>
//                   ))
//                 ) : logs.length === 0 ? (
//                   <tr>
//                     <td colSpan={7} className="px-6 py-16 text-center text-gray-400">
//                       <div className="flex flex-col items-center gap-2">
//                         <svg className="w-8 h-8 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
//                           <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
//                         </svg>
//                         <span className="text-sm">No audit log entries found</span>
//                       </div>
//                     </td>
//                   </tr>
//                 ) : (
//                   logs.map((log) => (
//                     <tr
//                       key={log.id}
//                       className="hover:bg-gray-50/80 transition-colors cursor-pointer"
//                       onClick={() => setSelectedLog(log)}
//                     >
//                       <td className="px-6 py-3.5 text-gray-600 whitespace-nowrap font-mono text-xs">
//                         {formatTimestamp(log.timestamp)}
//                       </td>
//                       <td className="px-6 py-3.5 font-medium text-gray-800">
//                         {formatAction(log.action)}
//                       </td>
//                       <td className="px-6 py-3.5">
//                         <span
//                           className={`inline-flex items-center text-xs px-2 py-0.5 rounded-full font-medium ${
//                             MODEL_TYPE_COLORS[log.model_type] || 'bg-gray-100 text-gray-700'
//                           }`}
//                         >
//                           {MODEL_TYPE_LABELS[log.model_type] || log.model_type}
//                         </span>
//                       </td>
//                       <td className="px-6 py-3.5 text-gray-500 font-mono text-xs">
//                         #{log.model_id}
//                       </td>
//                       <td className="px-6 py-3.5 text-gray-600 max-w-[200px] truncate">
//                         {log.user_email || <span className="text-gray-400 italic">System</span>}
//                       </td>
//                       <td className="px-6 py-3.5 text-gray-400 font-mono text-xs">
//                         {log.ip_address || '—'}
//                       </td>
//                       <td className="px-6 py-3.5 text-right">
//                         <button
//                           onClick={(e) => { e.stopPropagation(); setSelectedLog(log); }}
//                           className="text-xs text-blue-600 hover:text-blue-800 font-medium"
//                         >
//                           Details
//                         </button>
//                       </td>
//                     </tr>
//                   ))
//                 )}
//               </tbody>
//             </table>
//           </div>

//           {/* Pagination */}
//           {totalPages > 1 && (
//             <div className="flex items-center justify-between px-6 py-4 border-t border-gray-100 bg-gray-50/50">
//               <span className="text-sm text-gray-500">
//                 Page {page} of {totalPages} &middot; {totalCount.toLocaleString()} total entries
//               </span>
//               <div className="flex items-center gap-2">
//                 <button
//                   onClick={() => setPage((p) => Math.max(1, p - 1))}
//                   disabled={page === 1 || loading}
//                   className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
//                 >
//                   Previous
//                 </button>
//                 <button
//                   onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
//                   disabled={page === totalPages || loading}
//                   className="px-3 py-1.5 text-sm border border-gray-200 rounded-lg bg-white hover:bg-gray-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
//                 >
//                   Next
//                 </button>
//               </div>
//             </div>
//           )}
//         </div>
//       </div>

//       {/* Detail drawer */}
//       {selectedLog && (
//         <ChangesDrawer
//           log={selectedLog}
//           onClose={() => setSelectedLog(null)}
//         />
//       )}
//     </div>
//   );
// }