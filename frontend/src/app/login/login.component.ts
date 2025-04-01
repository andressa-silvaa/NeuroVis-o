import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgIf, NgClass } from '@angular/common';
import { Router, RouterModule } from '@angular/router'; 

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, NgIf, NgClass, RouterModule],
  templateUrl: './login.component.html',
  styleUrl: './login.component.css'
})
export class LoginComponent {

  emailInput: string = '';  
  senhaInput: string = ''; 

  constructor(private router: Router) { }

  onSubmit(form: any) {
    if (form.valid) {
      this.emailInput = '';
      this.senhaInput = '';
      console.log('Formulário válido', form.value);
    } else {
      console.log('Formulário inválido');
    }
  }
  
}