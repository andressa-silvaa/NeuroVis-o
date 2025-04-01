import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { FormsModule, NgForm } from '@angular/forms';
import { NgIf, NgClass } from '@angular/common';

@Component({
  selector: 'app-sign-up',
  standalone: true,
  imports: [RouterModule, FormsModule, NgIf, NgClass],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.css'
})
export class SignUpComponent {
  nomeInput: string = '';
  emailInput: string = '';
  senhaInput: string = '';
  senhaConfirmacaoInput: string = '';

  constructor(private router: Router) { }

  onSubmit(form: NgForm) {
    if (form.valid && this.senhaInput === this.senhaConfirmacaoInput) {
      console.log('Formulário válido', form.value);

      this.nomeInput = '';
      this.emailInput = '';
      this.senhaInput = '';
      this.senhaConfirmacaoInput = '';
      form.resetForm();
    }
  }
}