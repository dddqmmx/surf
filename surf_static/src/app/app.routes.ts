import { Routes } from '@angular/router';

export const routes: Routes = [
  {path:'',pathMatch:'full',redirectTo:'CustomersModule'},
  {path:'CustomersModule',loadChildren:()=>import('./customers/customers.module').then(m=>m.CustomersModule)}
];
