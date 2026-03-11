'use client'


import TopBar from "@/components/layout/TopBar";
import StatsCards from "../../components/dashboard/StartsCard";
import CasesTable from "../../components/cases/CasesTable";

export default function DashboardPage() {

const cases = [
 { id:1, title:"ABC Case", status:"active", client_name:"ABC Corp" },
 { id:2, title:"Doe Case", status:"closed", client_name:"John Doe" },
 { id:3, title:"XYZ Case", status:"pending", client_name:"XYZ Ltd" },
];

  return (
    <div>

      <TopBar title="Dashboard" />

      <div className="p-6">
        <StatsCards cases={cases} />
      </div>

      <div className="px-6 pb-6">
        <h2 className="text-lg font-semibold mb-4">Recent Cases</h2>

        <CasesTable
          cases={cases}
          isLoading={false}
          onEdit={() => {}}
          onDelete={() => {}}
        />
      </div>

    </div>
  );
}
// import TopBar from "@/components/layout/TopBar";
// import StatsCards from "../../components/dashboard/StartsCard";
// import CaseTable from "../../components/cases/CasesTable";



// export default function DashboardPage() {

//     const cases = [
//     { status: "active", client_name: "ABC Corp" },
//     { status: "closed", client_name: "John Doe" },
//     { status: "pending", client_name: "XYZ Ltd" },
//     { status: "active", client_name: "John Doe" },
//   ];



//   return (
//     <div>
//        <TopBar title="Dashboard" />


//         <div className="p-6">
//         <StatsCards cases={cases} />
//       </div>
//       <div className="p-6">Recent cases
//         <CaseTable cases={cases} />


//       </div>
    
//     </div>
//   );
// }