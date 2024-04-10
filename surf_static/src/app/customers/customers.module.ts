import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { CustomersRoutingModule } from './customers-routing.module';
import { HelloComponent } from './hello/hello.component';
import { ChatComponent } from './chat/chat.component';


@NgModule({
    declarations: [

    ],
    imports: [
        CommonModule,
        CustomersRoutingModule,
        HelloComponent,
        ChatComponent
    ]
})
export class CustomersModule { }
