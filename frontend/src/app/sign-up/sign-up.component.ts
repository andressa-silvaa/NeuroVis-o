import { Component } from '@angular/core';
import { Router, RouterModule } from '@angular/router';
import { FormsModule, NgForm } from '@angular/forms';
import { NgIf, NgClass } from '@angular/common';
import { ApiService } from '../services/api.service';
import { HttpClientModule } from '@angular/common/http';
import { ToastrService } from 'ngx-toastr';

@Component({
  selector: 'app-sign-up',
  standalone: true,
  imports: [RouterModule, FormsModule, NgIf, NgClass, HttpClientModule],
  templateUrl: './sign-up.component.html',
  styleUrl: './sign-up.component.css'
})
export class SignUpComponent {
  nomeInput: string = '';
  emailInput: string = '';
  senhaInput: string = '';
  senhaConfirmacaoInput: string = '';
  isLoading: boolean = false;

  constructor(
    private router: Router,
    private apiService: ApiService,
    private toastr: ToastrService
  ) { }

  onSubmit(form: NgForm) {
    if (form.valid && this.senhaInput === this.senhaConfirmacaoInput) {
      this.isLoading = true;

      const userData = {
        name: this.nomeInput,
        email: this.emailInput,
        password: this.senhaInput
      };

      this.apiService.post('users/register', userData)
        .subscribe({
          next: (response) => {
            this.toastr.success('Cadastro realizado com sucesso!', 'Sucesso');
            this.resetForm(form);
            this.router.navigate(['/login']); 
          },
          error: (error) => {
            this.handleApiError(error);
          },
          complete: () => {
            this.isLoading = false;
          }
        });
    }
  }

  private handleApiError(error: any) {
    if (error.status == 400) {
        const errorDetails = JSON.parse(error.message); 
        if (errorDetails && errorDetails.details) {
            if (errorDetails.details.email && errorDetails.details.email.includes('Email já cadastrado')) {
                this.toastr.warning('Já existe uma conta com este e-mail. Por favor, faça login ou utilize outro e-mail.', 'Cadastro existente');
                return;
            }
            this.showValidationErrors(errorDetails.details);
            return;
        } else {
            console.warn('A propriedade "details" não está disponível ou não tem a estrutura esperada.');
        }
    }

    this.toastr.error('Ocorreu um erro durante o cadastro. Por favor, tente novamente.', 'Erro');
  }
  
  private showValidationErrors(errorDetails: any) {
    const fieldNames: { [key: string]: string } = {
        'email': 'E-mail',
        'password': 'Senha',
        'name': 'Nome completo'
    };

    for (const field in errorDetails) {
        const errors = errorDetails[field];
        if (Array.isArray(errors)) {
            const fieldName = fieldNames[field] || field;
            errors.forEach((errorMsg: string) => {
                this.toastr.warning(`${fieldName}: ${errorMsg}`, 'Validação');
            });
        }
    }
  }

  private resetForm(form: NgForm) {
    this.nomeInput = '';
    this.emailInput = '';
    this.senhaInput = '';
    this.senhaConfirmacaoInput = '';
    form.resetForm();
  }
}