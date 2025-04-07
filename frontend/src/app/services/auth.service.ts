import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { catchError, Observable, of, tap, throwError } from 'rxjs';
import { AuthStateService } from './auth-state.service';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl: string = 'http://localhost:5000/api'; 

  constructor(
    private http: HttpClient, 
    private router: Router,
    private authStateService: AuthStateService
  ) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/login`, { email, password }, { withCredentials: true }).pipe(
      tap((response: any) => {
        this.authStateService.setAuthenticated(true);
        this.isAuthenticated().subscribe();
      }),
      catchError(error => {
        console.error('Erro ao realizar login:', error);
        return throwError(error);
      })
    );
  }

  logout(): void {
    this.http.post(`${this.baseUrl}/users/logout`, {}, { withCredentials: true }).subscribe({
      next: () => {
        this.authStateService.setAuthenticated(false);
      },
      error: (error) => {
        console.error('Erro ao realizar logout:', error); // Log de erro
      }
    });
  }

  isAuthenticated(): Observable<any> {
    return this.http.get<any>(`${this.baseUrl}/users/auth/check`, { 
      withCredentials: true,
      headers: {
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
      }
    }).pipe(
      tap(response => {
        console.log('Autenticação verificada:', response);
        this.authStateService.setAuthenticated(response.authenticated);
      }),
      catchError(error => {
        console.error('Erro na verificação:', error);
        this.authStateService.setAuthenticated(false);
        return of({ authenticated: false, error: error.message });
      })
    );
  }

  refreshAccessToken(): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/refresh`, {}, { withCredentials: true }).pipe(
      tap(response => {
      }),
      catchError(error => {
        console.error('Erro ao atualizar token de acesso:', error); // Log de erro
        this.logout(); 
        return throwError(error);
      })
    );
  }
}