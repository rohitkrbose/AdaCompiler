with Ada.Text_IO;
use Ada.Text_IO;

procedure arithmetic is
	x : integer;
	procedure main is
		k,i : integer;
		j,z : float;
	begin
		z := 2.0;
		j := 5.0;
		z := j*z + 2.3;
		-- k := 5;
		-- -- i := 5*k + i * (k + 5) ;
		-- k := k*i;
		-- print_int (k,i);
		print_float (z);
	end;
begin
	main;
end;