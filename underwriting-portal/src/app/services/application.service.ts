import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { environment } from '../../environments/environment';
import { Observable } from 'rxjs';

export type SmokingStatus = 'smoker' | 'non-smoker';

export interface ApplicantPayload {
  name: string;
  email?: string | null;
  contact_number?: string | null;
  age: number;
  income: number;
  occupation?: string | null;
  location?: string | null;
  prior_claims?: number;
  smoking_status: SmokingStatus;
}

export interface ApplicationCreatePayload {
  applicant: ApplicantPayload;
  product_type: string;
  coverage_amount: number;
}

export interface ApplicationCreateResponse {
  id?: number;
  application_id?: number;
}

@Injectable({ providedIn: 'root' })
export class ApplicationService {
  private base = environment.apiBaseUrl;
  constructor(private http: HttpClient) {}
  createApplication(payload: ApplicationCreatePayload): Observable<ApplicationCreateResponse> {
    return this.http.post<ApplicationCreateResponse>(`${this.base}/api/applications/`, payload);
  }
}
