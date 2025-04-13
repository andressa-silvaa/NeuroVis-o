import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { catchError, Observable, of, tap, throwError } from 'rxjs';
import { AuthStateService } from './auth-state.service';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl: string = environment.apiUrl; 

  constructor(
    private http: HttpClient, 
    private router: Router,
    private authStateService: AuthStateService
  ) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/login`, { email, password }).pipe(
      tap((response: any) => {
        this.storeTokens(response);
        this.authStateService.setAuthenticated(true);
      }),
      catchError(error => {
        return throwError(error);
      })
    );
  }

  logout(): void {
    sessionStorage.removeItem('access_token');
    sessionStorage.removeItem('refresh_token');
    this.authStateService.setAuthenticated(false);
    this.router.navigate(['/login']);
  }

  isAuthenticated(): Observable<any> {
    const token = this.getAccessToken();
    if (!token) {
      return of({ authenticated: false });
    }
    
    return this.http.get<any>(`${this.baseUrl}/users/auth/check`, {
      headers: {
        'Authorization': `Bearer ${token}` 
      }
    }).pipe(
      tap(response => {
        this.authStateService.setAuthenticated(response.authenticated);
      }),
      catchError(error => {
        this.authStateService.setAuthenticated(false);
        return of({ authenticated: false, error: error.message });
      })
    );
  }

  refreshAccessToken(): Observable<any> {
    const refreshToken = this.getRefreshToken();
    if (!refreshToken) {
      this.logout();
      return throwError(() => new Error('No refresh token available'));
    }

    return this.http.post(`${this.baseUrl}/users/refresh`, {}, {
      headers: {
        'Authorization': `Bearer ${refreshToken}`
      }
    }).pipe(
      tap((response: any) => {
        sessionStorage.setItem('access_token', response.access_token);
      }),
      catchError(error => {
        this.logout(); 
        return throwError(error);
      })
    );
  }

  private storeTokens(response: any): void {
    sessionStorage.setItem('access_token', response.access_token);
    sessionStorage.setItem('refresh_token', response.refresh_token);
  }

  getAccessToken(): string | null {
    return sessionStorage.getItem('access_token');
  }

  getRefreshToken(): string | null {
    return sessionStorage.getItem('refresh_token');
  }
}