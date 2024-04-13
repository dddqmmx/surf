import { Component } from '@angular/core';
import {NgForOf} from "@angular/common";

@Component({
  selector: 'app-main',
  standalone: true,
    imports: [
        NgForOf
    ],
  templateUrl: './main.component.html',
  styleUrl: './main.component.css'
})
export class MainComponent {
    data = {
        objects: [
            {
                user: {
                    user_nickname: "兎田ぺこら",
                    user_info: {"email": "woshishabi@gmail.com", "phone": "1145141919810"}
                },
            },
            {
                user: {
                    user_nickname: "白上フブキ",
                    user_info: {"email": "woshishabi@gmail.com", "phone": "1145141919810"}
                },
            }
        ]
    };
}
