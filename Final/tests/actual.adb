with Ada.Text_IO;
use Ada.Text_IO;

procedure actual is
	q : Integer;
	procedure Write_A_Line (A, B: Integer) is
		u : Integer;
	begin
	   u := 5;
	end;
	function Minimum (A, B: Integer) return Integer is
		C : Integer;
		D : Float;
	begin
	   if A <= B then
	   	C := A;
	   else
	     C := B;
	   end if;
	   q := 5;
	   return C;
	end;
	procedure main is
		z : Integer;
	begin
		Write_A_Line(5,9);
		q := Minimum(q,4);
	end;
begin
	main;
end;