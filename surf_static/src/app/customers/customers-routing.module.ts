import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { HelloComponent } from './hello/hello.component';
import { ChatComponent } from './chat/chat.component';
import { LoginComponent } from './login/login.component';
import {MainComponent} from "./main/main.component";
import {IntroduceComponent} from "./introduce/introduce.component";


const routes: Routes = [
    {path: '', component:IntroduceComponent},
    {path:"hello",component:HelloComponent},
    {path:"chat",component:ChatComponent},
    {
        path:"main",
        component:MainComponent,
        children:[
            {path:"chat/:id",component:ChatComponent}
        ]
    },
    {path:"login",component:LoginComponent}
];

@NgModule({
    imports: [RouterModule.forChild(routes)],
    exports: [RouterModule]
})
export class CustomersRoutingModule { }
