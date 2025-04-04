import { Injectable } from '@angular/core';
import { CanActivate, Router } from '@angular/router';
import { AuthService } from '../services/auth.service'; 
import { Observable } from 'rxjs';
import { map, catchError } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class AuthGuard implements CanActivate {
  constructor(private authService: AuthService, private router: Router) {}

  canActivate(): Observable<boolean> {
    return this.authService.isAuthenticated().pipe(
      map(response => {
        if (response.authenticated) {
          return true; 
        } else {
          this.router.navigate(['/login']); 
          return false; 
        }
      }),
      catchError(() => {
        this.router.navigate(['/login']); 
        return [false]; 
      })
    );
  }
}