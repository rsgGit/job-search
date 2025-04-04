import { inject } from '@angular/core';
import { HttpInterceptorFn } from '@angular/common/http';
import { finalize } from 'rxjs/operators';
import { LoaderService } from '../shared/loader/loader.service';

export const loaderInterceptor: HttpInterceptorFn = (req, next) => {
  const loaderService = inject(LoaderService);

  setTimeout(() => {
    loaderService.show();
  }, 0);

  return next(req).pipe(finalize(() => 
  {
    setTimeout(() => {
      loaderService.hide();
    }, 0);
  }
));
};
