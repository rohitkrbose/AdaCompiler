with Ada.Text_IO;
use Ada.Text_IO;

procedure demo is
	x : integer;
	procedure main is
		k,i : integer;
		j,z : float;
	begin
		x := 90;
		k := 4;
		z := 2.0;
		j := 5.0 * x;
		-- z := j*z + 2.3;
		-- k := k + x;
		print_int (x);
		print_int (k);
		print_float (j);
		print_float (z);
		-- k := 5;
		-- -- i := 5*k + i * (k + 5) ;
		-- k := k*i;
		-- print_int (k,i);
		-- print_float (z);
	end;
begin
	main;
end;