import { Routes } from "@angular/router";
import {LoginComponent} from "./pages/login/login.component";
import {MainComponent} from "./pages/main/main.component";

export const routes: Routes = [
    {path:'', component:LoginComponent},
    {path:'main', component:MainComponent}
];
