import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { ToastrService } from 'ngx-toastr';
import { Observable } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private baseUrl: string = 'http://localhost:5000/api'; 

  constructor(private http: HttpClient, private router: Router, private toastr: ToastrService) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/login`, { email, password }, { withCredentials: true });
  }

  logout(): void {
    this.http.post(`${this.baseUrl}/users/logout`, {}, { withCredentials: true }).subscribe(() => {
      this.router.navigate(['/login']);
    });
  }

  isAuthenticated(): Observable<any> {
    return this.http.get(`${this.baseUrl}/auth/check`, { withCredentials: true });
  }

  refreshAccessToken(): Observable<any> {
    return this.http.post(`${this.baseUrl}/users/refresh`, {}, { withCredentials: true });
  }
}