import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { NgIf, NgClass } from '@angular/common';
import { Router, RouterModule, NavigationEnd } from '@angular/router';  
import { AuthService } from '../services/auth.service'; 
import { ToastrService } from 'ngx-toastr'; 

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [FormsModule, NgIf, NgClass, RouterModule],
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.css']
})
export class LoginComponent {
  emailInput: string = '';  
  senhaInput: string = '';  
  isLoading: boolean = false;  

  constructor(
    private router: Router, 
    private authService: AuthService, 
    private toastr: ToastrService
  ) { 
    this.router.events.subscribe(event => {
      if (event instanceof NavigationEnd) {
        this.isLoading = false;
      }
    });
  }

  onSubmit(form: any) {
    if (form.valid) {
      this.isLoading = true;  
      this.authService.login(this.emailInput, this.senhaInput).subscribe({
        next: (response) => {
          this.toastr.success('Login realizado com sucesso!', 'Sucesso');
          this.router.navigate(['/upload-image']);
          form.reset();  
        },
        error: (error) => {
          console.error('Erro no login:', error);
          this.isLoading = false;  
          if (error.status == 401) {
            this.toastr.error('Credenciais inválidas. Tente novamente.', 'Erro de Login');
          } else {
            this.toastr.error('Ocorreu um erro ao tentar fazer login. Por favor, tente novamente.', 'Erro');
          }
        }
      });
    } else {
      console.log('Formulário inválido');
    }
  }
}
