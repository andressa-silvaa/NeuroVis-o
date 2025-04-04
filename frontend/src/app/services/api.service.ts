import { Injectable } from '@angular/core';
import { HttpClient, HttpParams, HttpHeaders,HttpErrorResponse } 
from '@angular/common/http';
import { Observable, catchError, throwError } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class ApiService {
  private readonly baseUrl = 'http://localhost:5000/api'; 

  constructor(private http: HttpClient) { }

  get<T>(endpoint: string, params?: any, headers?: any): Observable<T> {
    const url = `${this.baseUrl}/${endpoint}`;
    const options = {
      params: this.buildParams(params),
      headers: new HttpHeaders(headers)
    };

    return this.http.get<T>(url, options)
      .pipe(
        catchError(this.handleError)
      );
  }

  post<T>(endpoint: string, body: any, headers?: any): Observable<T> {
    const url = `${this.baseUrl}/${endpoint}`;
    return this.http.post<T>(url, body, { headers: new HttpHeaders(headers) })
      .pipe(
        catchError(this.handleError)
      );
  }

  put<T>(endpoint: string, body: any, headers?: any): Observable<T> {
    const url = `${this.baseUrl}/${endpoint}`;
    return this.http.put<T>(url, body, { headers: new HttpHeaders(headers) })
      .pipe(
        catchError(this.handleError)
      );
  }

  delete<T>(endpoint: string, headers?: any): Observable<T> {
    const url = `${this.baseUrl}/${endpoint}`;
    return this.http.delete<T>(url, { headers: new HttpHeaders(headers) })
      .pipe(
        catchError(this.handleError)
      );
  }

  private buildParams(params: any): HttpParams {
    let httpParams = new HttpParams();
    if (params) {
      Object.keys(params).forEach(key => {
        httpParams = httpParams.append(key, params[key]);
      });
    }
    return httpParams;
  }
 
  private handleError(error: HttpErrorResponse) {
    let errorMessage: string;

    if (error.error instanceof ErrorEvent) {
        // Erro do lado do cliente
        errorMessage = error.error.message;
    } else {
        // Erro do lado do servidor
        errorMessage = error.error ? JSON.stringify(error.error) : error.message || 'Erro desconhecido';
    }
    return throwError(() => ({
        status: error.status,
        message: errorMessage
    }));
  }
}